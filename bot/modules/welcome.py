from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
from bot.database.session import get_session
from bot.database.models import Group

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == "private":
        return True
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group or not group.welcome_enabled:
        session.close()
        return

    welcome_text = group.welcome_text

    for member in update.message.new_chat_members:
        text = welcome_text.replace("{name}", member.full_name).replace("{mention}", member.mention_html())
        await update.message.reply_text(text, parse_mode="HTML")

    session.close()

async def set_welcome_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ شما دسترسی لازم برای این کار را ندارید.")
        return

    if not context.args:
        await update.message.reply_text("💡 برای تغییر متن خوشامدگویی، متن جدید را بعد از دستور بنویسید.\nمثال: `/setwelcome سلام {mention} عزیز به گروه ما خوش اومدی`", parse_mode="Markdown")
        return

    new_text = " ".join(context.args)
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)

    group.welcome_text = new_text
    session.commit()
    await update.message.reply_text("✅ متن خوشامدگویی با موفقیت تغییر یافت.")
    session.close()

async def welcome_toggle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        status = "فعال" if group.welcome_enabled else "غیرفعال"
        await update.message.reply_text(f"📊 وضعیت خوشامدگویی در این گروه: {status}\nبرای تغییر: `/welcome on` یا `/welcome off`", parse_mode="Markdown")
        session.close()
        return

    action = context.args[0].lower()
    if action == "on":
        group.welcome_enabled = True
        await update.message.reply_text("✅ ارسال پیام خوشامدگویی فعال شد.")
    elif action == "off":
        group.welcome_enabled = False
        await update.message.reply_text("🔓 ارسال پیام خوشامدگویی غیرفعال شد.")
    else:
        await update.message.reply_text("❌ دستور نامعتبر. از on یا off استفاده کنید.")

    session.commit()
    session.close()

def get_welcome_handlers():
    return [
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member),
        CommandHandler("setwelcome", set_welcome_cmd),
        CommandHandler("welcome", welcome_toggle_cmd),
    ]
