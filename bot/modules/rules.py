from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin, get_group

async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    if not group.rules:
        await update.effective_message.reply_text("📜 قوانین برای این گروه تنظیم نشده است.")
    else:
        await update.effective_message.reply_text(f"📜 قوانین گروه {group.title}:\n\n{group.rules}", parse_mode=None)
    session.close()
    raise ApplicationHandlerStop()

async def set_rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args:
        await update.effective_message.reply_text("💡 مثال: /setrules قوانین گروه ما...")
        raise ApplicationHandlerStop()
    new_rules = " ".join(context.args)
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    group.rules = new_rules
    session.commit()
    await update.effective_message.reply_text("✅ قوانین گروه بروزرسانی شد.")
    session.close()
    raise ApplicationHandlerStop()

async def rules_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text("🛡 تنظیمات قوانین فقط داخل گروه قابل استفاده است.")
        raise ApplicationHandlerStop()
    if not await is_admin(update, context):
        await update.effective_message.reply_text("❌ این بخش فقط برای مدیران گروه است.")
        raise ApplicationHandlerStop()
    text = update.effective_message.text

    if text == "🔘 فعال/غیرفعال سازی قوانین":
        session = get_session()
        try:
            group = get_group(session, update.effective_chat.id, update.effective_chat.title)
            group.rules_enabled = not bool(group.rules_enabled)
            session.commit()
            status = "فعال" if group.rules_enabled else "غیرفعال"
        finally:
            session.close()
        await update.effective_message.reply_text(f"📜 نمایش قوانین {status} شد.")
        raise ApplicationHandlerStop()
    if text == "📝 تغییر متن قوانین":
        await update.effective_message.reply_text("💡 برای تغییر قوانین بنویسید:\n\n/setrules [متن قوانین شما]")
        raise ApplicationHandlerStop()

def get_rules_handlers():
    rules_triggers = "^(قوانین|قوانین گروه چیه؟|قوانین رو بفرست|rules)$"
    return [
        CommandHandler("rules", rules_cmd),
        CommandHandler("setrules", set_rules_cmd),
        MessageHandler(filters.TEXT & filters.Regex(rules_triggers), rules_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(🔘 فعال/غیرفعال سازی قوانین|📝 تغییر متن قوانین)$"), rules_settings_handler),
    ]
