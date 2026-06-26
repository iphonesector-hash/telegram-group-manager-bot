from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User, Warning, Group
from bot.modules.economy import rank_cmd

async def count_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return
    if update.message.text and update.message.text.startswith('/'):
        return

    session = get_session()
    user_id = update.effective_user.id
    user = session.query(User).filter(User.id == user_id).first()

    if user:
        user.message_count += 1
        user.coins += 1
        user.xp += 5
        new_level = (user.xp // 100) + 1
        if new_level > user.level:
            user.level = new_level
        try:
            session.commit()
        except:
            session.rollback()
    session.close()

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    user_obj = update.effective_user
    session = get_session()
    user = session.query(User).filter(User.id == user_obj.id).first()

    if not user:
        await update.message.reply_text("❌ ابتدا پیامی بفرستید تا پروفایل شما ساخته شود.")
        session.close()
        return

    rank = session.query(User).filter(User.coins > user.coins).count() + 1
    warn_count = 0
    if update.effective_chat and update.effective_chat.type != "private":
        warn_count = session.query(Warning).filter(
            Warning.user_id == user.id,
            Warning.group_id == update.effective_chat.id
        ).count()

    join_date = user.joined_at.strftime("%Y-%m-%d")

    text = (
        f"👤 **پروفایل {user_obj.full_name}**\n\n"
        f"🆔 شناسه: `{user.id}`\n"
        f"👤 نام کاربری: @{user_obj.username if user_obj.username else 'ندارد'}\n"
        f"📅 تاریخ عضویت: {join_date}\n"
        f"🌟 سطح: {user.level}\n"
        f"✨ امتیاز (XP): {user.xp}\n"
        f"📨 تعداد پیام‌ها: {user.message_count}\n"
        f"🪙 سکه‌ها: {user.coins}\n"
        f"🏆 رتبه جهانی: {rank}\n"
        f"⚠️ تعداد اخطارها (در این گروه): {warn_count}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    session.close()

async def user_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📊 پروفایل من":
        await profile_cmd(update, context)
    elif text == "🏆 رتبه جهانی":
        await rank_cmd(update, context)
    elif text == "📜 سوابق اخطار":
        from bot.modules.warnings import warns_cmd
        await warns_cmd(update, context)

def get_profile_handlers():
    return [
        CommandHandler("profile", profile_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(📊 پروفایل من|🏆 رتبه جهانی|📜 سوابق اخطار)$"), user_button_handler),
        MessageHandler(filters.ALL & ~filters.COMMAND, count_message),
    ]
