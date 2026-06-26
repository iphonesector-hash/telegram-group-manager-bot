from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User, Warning, Group
from bot.modules.economy import rank_cmd
from bot.utils.helpers import get_reply_text, get_user_badge

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
        user.xp += 5
        # Dynamic Level Up
        next_lv_xp = user.level * 100 * (1.1 ** (user.level-1))
        if user.xp >= next_lv_xp:
            user.level += 1
        user.coins += 1
        try:
            session.commit()
        except:
            session.rollback()
    session.close()

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user: return
    user_obj = update.effective_user
    session = get_session()
    user = session.query(User).filter(User.id == user_obj.id).first()

    if not user:
        await update.effective_message.reply_text("❌ پروفایل شما یافت نشد.")
        session.close()
        return

    rank = session.query(User).filter(User.coins > user.coins).count() + 1
    badge = get_user_badge(user)

    text = (
        f"⚡ **Sector Profile**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 نام: {user_obj.full_name}\n"
        f"🆔 شناسه: `{user.id}`\n"
        f"🏅 نشان: {badge}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌟 سطح: {user.level}\n"
        f"✨ امتیاز: {user.xp}\n"
        f"🪙 سکه: {user.coins}\n"
        f"📨 پیام: {user.message_count}\n"
        f"🏆 رتبه: {rank}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    reply = await get_reply_text(user_obj, text)
    await update.effective_message.reply_text(reply, parse_mode=None)
    session.close()

async def group_stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text("❌ فقط در گروه‌ها کاربرد دارد.")
        return

    session = get_session()
    m_count = await context.bot.get_chat_member_count(update.effective_chat.id)

    text = (
        f"📊 **آمار گروه {update.effective_chat.title}**\n\n"
        f"👥 اعضا: {m_count}\n"
        f"🤖 وضعیت: آنلاین 🟢\n"
        f"⚙️ پلتفرم: SectorBot 2.0"
    )
    await update.effective_message.reply_text(text, parse_mode=None)
    session.close()

def get_profile_handlers():
    return [
        CommandHandler("profile", profile_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(👤 پروفایل|🏆 رتبه جهانی|📜 سوابق اخطار|📊 آمار گروه)$"), profile_cmd),
        MessageHandler(filters.ALL & ~filters.COMMAND, count_message),
    ]
