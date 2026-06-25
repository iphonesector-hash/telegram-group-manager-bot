from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User, Warning

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
        except Exception as e:
            print(f"❌ Error updating user stats: {e}")
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

    # Count warns in this group (if in a group)
    warn_count = 0
    if update.effective_chat and update.effective_chat.type != "private":
        warn_count = session.query(Warning).filter(
            Warning.user_id == user.id,
            Warning.group_id == update.effective_chat.id
        ).count()

    text = (
        f"👤 **پروفایل {user_obj.full_name}**\n\n"
        f"🆔 شناسه: `{user.id}`\n"
        f"👤 نام کاربری: @{user_obj.username if user_obj.username else 'ندارد'}\n"
        f"🌟 سطح: {user.level}\n"
        f"✨ امتیاز (XP): {user.xp}\n"
        f"📨 تعداد پیام‌ها: {user.message_count}\n"
        f"🪙 سکه‌ها: {user.coins}\n"
        f"⚠️ تعداد اخطارها (در این گروه): {warn_count}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    session.close()

async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    session = get_session()
    try:
        top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()

        if not top_users:
            await update.message.reply_text("هنوز کسی امتیاز نگرفته.")
            return

        lines = []
        for i, user in enumerate(top_users, start=1):
            name = user.first_name or "نامشخص"
            lines.append(f"{i}. {name} — 🪙 {user.coins} (سطح {user.level})")

        await update.message.reply_text("🏆 **برترین‌ها (بر اساس سکه):**\n\n" + "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        print(f"❌ Error fetching top users: {e}")
        await update.message.reply_text("❌ خطا در دریافت اطلاعات.")
    finally:
        session.close()

def get_profile_handlers():
    return [
        CommandHandler("profile", profile_cmd),
        CommandHandler("top", top_cmd),
        MessageHandler(filters.ALL & ~filters.COMMAND, count_message),
    ]
