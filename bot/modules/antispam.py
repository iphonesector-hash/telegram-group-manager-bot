from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group, Mute
from bot.utils.helpers import is_admin
import time
import datetime

user_messages = {} # {(group_id, user_id): [timestamps]}

async def antispam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not update.effective_chat:
        return

    if await is_admin(update, context):
        return

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group or not group.antispam_enabled:
        session.close()
        return

    user_id = update.effective_user.id
    group_id = update.effective_chat.id
    key = (group_id, user_id)
    now = time.time()

    if key not in user_messages:
        user_messages[key] = []

    user_messages[key] = [t for t in user_messages[key] if now - t < 10]
    user_messages[key].append(now)

    if len(user_messages[key]) > group.antispam_limit:
        try:
            await update.message.delete()

            until = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) + datetime.timedelta(minutes=15)

            mute = session.query(Mute).filter(Mute.user_id == user_id, Mute.group_id == group_id).first()
            if not mute:
                mute = Mute(user_id=user_id, group_id=group_id, until=until)
                session.add(mute)
            else:
                mute.until = until
            session.commit()

            await update.effective_chat.restrict_member(user_id, ChatPermissions(can_send_messages=False), until_date=until)
            await update.message.reply_text(f"⚠️ کاربر {update.effective_user.first_name} به دلیل اسپم به مدت ۱۵ دقیقه بی‌صدا شد.")

            session.close()
            raise ApplicationHandlerStop()
        except ApplicationHandlerStop:
            raise
        except:
            pass

    session.close()

async def antispam_toggle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)

    if not context.args:
        status = "فعال" if group.antispam_enabled else "غیرفعال"
        await update.message.reply_text(f"📊 وضعیت ضد اسپم: {status}\nبرای تغییر: `/antispam on` یا `/antispam off`", parse_mode="Markdown")
        session.close()
        return

    action = context.args[0].lower()
    if action == "on":
        group.antispam_enabled = True
        await update.message.reply_text("✅ سیستم ضد اسپم فعال شد.")
    elif action == "off":
        group.antispam_enabled = False
        await update.message.reply_text("🔓 سیستم ضد اسپم غیرفعال شد.")
    else:
        await update.message.reply_text("❌ دستور نامعتبر. از on یا off استفاده کنید.")

    session.commit()
    session.close()

def get_antispam_handlers():
    return [
        CommandHandler("antispam", antispam_toggle_cmd),
        MessageHandler(filters.ALL, antispam_filter), # Remove ~filters.COMMAND to block spammy commands
    ]
