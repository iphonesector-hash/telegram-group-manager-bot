from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group, Mute
from bot.utils.helpers import is_admin, get_group
import time
import datetime

user_messages = {}

async def antispam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_user or not update.effective_chat:
        return
    if await is_admin(update, context): return

    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    if not group.antispam_enabled:
        session.close()
        return

    user_id = update.effective_user.id
    group_id = update.effective_chat.id
    key = (group_id, user_id)
    now = time.time()

    if key not in user_messages: user_messages[key] = []
    user_messages[key] = [t for t in user_messages[key] if now - t < 10]
    user_messages[key].append(now)

    if len(user_messages[key]) > group.antispam_limit:
        try:
            await update.effective_message.delete()
            until = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=15)
            mute = session.query(Mute).filter(Mute.user_id == user_id, Mute.group_id == group_id).first()
            if not mute:
                mute = Mute(user_id=user_id, group_id=group_id, until=until)
                session.add(mute)
            else:
                mute.until = until
            session.commit()
            await update.effective_chat.restrict_member(user_id, ChatPermissions(can_send_messages=False), until_date=until)
            await update.effective_chat.send_message(f"⚠️ کاربر {update.effective_user.first_name} به دلیل اسپم به مدت ۱۵ دقیقه بی‌صدا شد.")
            session.close()
            raise ApplicationHandlerStop()
        except ApplicationHandlerStop: raise
        except: pass
    session.close()

async def antispam_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    group.antispam_enabled = not group.antispam_enabled
    session.commit()
    status = "فعال" if group.antispam_enabled else "غیرفعال"
    await update.effective_message.reply_text(f"🛡 وضعیت ضد اسپم به **{status}** تغییر یافت.", parse_mode="Markdown")
    session.close()
    raise ApplicationHandlerStop()

def get_antispam_handlers():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^🛡 ضد اسپم$"), antispam_button_handler),
        MessageHandler(filters.ALL & ~filters.COMMAND, antispam_filter),
    ]
