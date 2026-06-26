import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin, get_group

# In-memory tracking for smart anti-spam
user_messages = {} # {chat_id: {user_id: [timestamps]}}
last_text = {} # {chat_id: {user_id: (text, count)}}

async def antispam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_user or not update.effective_chat:
        return

    if await is_admin(update, context):
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    current_time = time.time()

    session = get_session()
    group = get_group(session, chat_id, update.effective_chat.title)

    if not group.antispam_enabled:
        session.close()
        return

    # 1. Flood Detection (Messages per time)
    if chat_id not in user_messages:
        user_messages[chat_id] = {}
    if user_id not in user_messages[chat_id]:
        user_messages[chat_id][user_id] = []

    timestamps = user_messages[chat_id][user_id]
    timestamps.append(current_time)

    # Filter for last 10 seconds
    timestamps = [t for t in timestamps if current_time - t < 10]
    user_messages[chat_id][user_id] = timestamps

    if len(timestamps) > 5: # More than 5 messages in 10s
        try:
            await update.effective_message.delete()
        except:
            pass
        session.close()
        raise ApplicationHandlerStop()

    # 2. Repeated Message Detection
    text = update.effective_message.text or ""
    if len(text) > 5:
        if chat_id not in last_text:
            last_text[chat_id] = {}

        prev_text, count = last_text[chat_id].get(user_id, ("", 0))
        if text == prev_text:
            count += 1
            if count >= 3:
                try:
                    await update.effective_message.delete()
                except:
                    pass
                last_text[chat_id][user_id] = (text, count)
                session.close()
                raise ApplicationHandlerStop()
            last_text[chat_id][user_id] = (text, count)
        else:
            last_text[chat_id][user_id] = (text, 1)

    session.close()

async def antispam_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    group.antispam_enabled = not group.antispam_enabled
    session.commit()
    status = "فعال" if group.antispam_enabled else "غیرفعال"
    await update.effective_message.reply_text(f"🛡 وضعیت ضد اسپم به {status} تغییر یافت.", parse_mode=None)
    session.close()
    raise ApplicationHandlerStop()

def get_antispam_handlers():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^🛡 ضد اسپم$"), antispam_button_handler),
        MessageHandler(filters.ALL & ~filters.COMMAND, antispam_filter),
    ]
