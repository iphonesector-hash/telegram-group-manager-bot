import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin, get_group

user_messages = {} # {chat_id: {user_id: [timestamps]}}

async def antispam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_user or not update.effective_chat:
        return

    if await is_admin(update, context):
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    now = time.time()

    session = get_session()
    group = get_group(session, chat_id)
    if not group.antispam_enabled:
        session.close()
        return
    session.close()

    if chat_id not in user_messages: user_messages[chat_id] = {}
    if user_id not in user_messages[chat_id]: user_messages[chat_id][user_id] = []

    msg_history = user_messages[chat_id][user_id]
    msg_history.append(now)
    # Filter last 5 seconds
    msg_history = [t for t in msg_history if now - t < 5]
    user_messages[chat_id][user_id] = msg_history

    if len(msg_history) > 4: # limit 4 msg per 5s
        try:
            await update.effective_message.delete()
        except:
            pass
        raise ApplicationHandlerStop()

async def antispam_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    session = get_session()
    group = get_group(session, update.effective_chat.id)
    group.antispam_enabled = not group.antispam_enabled
    session.commit()
    status = "فعال" if group.antispam_enabled else "غیرفعال"
    await update.effective_message.reply_text(f"🛡 وضعیت ضد اسپم: {status}")
    session.close()
    raise ApplicationHandlerStop()

def get_antispam_handlers():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^🛡 ضد اسپم$"), antispam_button_handler),
        MessageHandler(filters.ALL & ~filters.COMMAND, antispam_filter),
    ]
