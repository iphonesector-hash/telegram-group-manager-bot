from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User

async def count_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user_id = update.effective_user.id
    user = session.query(User).filter(User.id == user_id).first()

    if user:
        user.message_count += 1
        user.coins += 1
        user.xp += 5

        # Simple leveling logic
        new_level = (user.xp // 100) + 1
        if new_level > user.level:
            user.level = new_level
            # Optionally notify user about level up

        session.commit()
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

    text = (
        f"👤 پروفایل {user_obj.full_name}\n"
        f"🆔 شناسه: `{user.id}`\n"
        f"🌟 سطح: {user.level}\n"
        f"✨ امتیاز (XP): {user.xp}\n"
        f"📨 تعداد پیام‌ها: {user.message_count}\n"
        f"🪙 سکه‌ها: {user.coins}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    session.close()

async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    session = get_session()
    top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()

    if not top_users:
        await update.message.reply_text("هنوز کسی امتیاز نگرفته.")
        session.close()
        return

    lines = []
    for i, user in enumerate(top_users, start=1):
        name = user.first_name or "نامشخص"
        lines.append(f"{i}. {name} ({user.id}) — 🪙 {user.coins} (Lvl {user.level})")

    await update.message.reply_text("🏆 برترین‌ها (بر اساس سکه):\n\n" + "\n".join(lines))
    session.close()

def get_profile_handlers():
    return [
        CommandHandler("profile", profile_cmd),
        CommandHandler("top", top_cmd),
        MessageHandler(filters.ALL & ~filters.COMMAND, count_message),
    ]
