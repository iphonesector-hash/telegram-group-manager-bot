from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin, get_group

async def antispam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_user:
        return

    if await is_admin(update, context):
        return

    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    if not group.antispam_enabled:
        session.close()
        return

    # Simple logic to be expanded later
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
