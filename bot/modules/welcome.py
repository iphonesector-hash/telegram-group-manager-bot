from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin, get_group

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    if not group.welcome_enabled:
        session.close()
        return

    welcome_text = group.welcome_text
    for member in update.message.new_chat_members:
        text = welcome_text.replace("{name}", member.full_name).replace("{mention}", member.mention_html())
        # HTML mention is usually safe if formatted correctly, but let's keep it for now as it's not AI output
        try:
            await update.message.reply_text(text, parse_mode="HTML")
        except:
            await update.message.reply_text(text, parse_mode=None)
    session.close()

async def welcome_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    group.welcome_enabled = not group.welcome_enabled
    session.commit()
    status = "فعال" if group.welcome_enabled else "غیرفعال"
    await update.message.reply_text(f"🌟 وضعیت خوشامدگویی به {status} تغییر یافت.", parse_mode=None)
    session.close()
    raise ApplicationHandlerStop()

async def set_welcome_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args:
        await update.message.reply_text("💡 مثال: /setwelcome سلام {mention}")
        return
    new_text = " ".join(context.args)
    session = get_session()
    group = get_group(session, update.effective_chat.id, update.effective_chat.title)

    group.welcome_text = new_text
    session.commit()
    await update.message.reply_text("✅ متن خوشامدگویی تغییر یافت.")
    session.close()

def get_welcome_handlers():
    return [
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member),
        MessageHandler(filters.TEXT & filters.Regex("^🌟 خوشامدگویی$"), welcome_button_handler),
        CommandHandler("setwelcome", set_welcome_cmd),
    ]
