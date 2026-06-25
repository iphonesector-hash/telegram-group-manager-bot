from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
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
        await update.message.reply_text(f"📜 قوانین گروه {group.title}:\n\n{group.rules}")

    session.close()

async def set_rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("💡 برای ثبت قوانین، متن قوانین را بعد از دستور بنویسید.\nمثال: `/setrules 1. فحش ندهید`", parse_mode="Markdown")
        return

    new_rules = " ".join(context.args)
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)

    group.rules = new_rules
    session.commit()
    await update.message.reply_text("✅ قوانین گروه با موفقیت ثبت شد.")
    session.close()

def get_rules_handlers():
    return [
        CommandHandler("rules", rules_cmd),
        CommandHandler("setrules", set_rules_cmd),
    ]
