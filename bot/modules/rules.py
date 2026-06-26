from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin

async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
    if not group or not group.rules:
        await update.message.reply_text("❌ قوانینی برای این گروه ثبت نشده است.")
    else:
        await update.message.reply_text(f"📜 **قوانین گروه {group.title}:**\n\n{group.rules}", parse_mode="Markdown")
    session.close()

async def rules_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rules_cmd(update, context)

def get_rules_handlers():
    return [
        CommandHandler("rules", rules_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^📜 قوانین$"), rules_button_handler),
    ]
