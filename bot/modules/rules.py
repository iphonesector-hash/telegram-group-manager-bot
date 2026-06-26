from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import get_group, is_admin
from bot.utils.keyboards import get_locks_menu

async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)
    if not group.rules:
        await update.effective_message.reply_text("❌ قوانینی برای این گروه ثبت نشده است.")
    else:
        await update.effective_message.reply_text(f"📜 **قوانین گروه {group.title}:**\n\n{group.rules}", parse_mode="Markdown")
    session.close()

async def rules_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text == "📜 قوانین":
        await rules_cmd(update, context)
    elif text == "🔗 ضد لینک":
        if await is_admin(update, context):
            await update.effective_message.reply_text("💡 برای مدیریت ضد لینک به بخش **قفل‌ها** مراجعه کنید.", reply_markup=get_locks_menu())
    raise ApplicationHandlerStop()

def get_rules_handlers():
    return [
        CommandHandler("rules", rules_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(📜 قوانین|🔗 ضد لینک)$"), rules_button_handler),
    ]
