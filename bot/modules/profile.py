from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import User, Warning, Group
from bot.modules.economy import rank_cmd
from bot.utils.helpers import get_reply_text

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
        # Real progression
        xp_gain = 5
        user.xp += xp_gain

        # Level increase logic
        next_level_xp = user.level * 100 * (1.2 ** (user.level - 1))
        if user.xp >= next_level_xp:
            user.level += 1
            # Optional: notify user in private

        user.coins += 1
        try:
            session.commit()
        except:
            session.rollback()
    session.close()

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    user_obj = update.effective_user
    session = get_session()
    user = session.query(User).filter(User.id == user_obj.id).first()

    if not user:
        await update.effective_message.reply_text("❌ ابتدا پیامی بفرستید تا پروفایل شما ساخته شود.")
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

    # Text-based Profile Card
    text = (
        f"👤 **Sector Profile**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 شناسه: `{user.id}`\n"
        f"👤 نام: {user_obj.full_name}\n"
        f"🏷 یوزرنیم: @{user_obj.username if user_obj.username else 'ندارد'}\n"
        f"📅 عضویت: {join_date}\n\n"
        f"🌟 سطح: {user.level}\n"
        f"✨ امتیاز (XP): {user.xp}\n"
        f"📨 پیام‌ها: {user.message_count}\n"
        f"🪙 سکه‌ها: {user.coins}\n"
        f"🏆 رتبه جهانی: {rank}\n"
        f"⚠️ اخطارها: {warn_count}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    reply = await get_reply_text(user_obj, text)
    await update.effective_message.reply_text(reply, parse_mode=None)
    session.close()

async def group_stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text("❌ این آمار مخصوص گروه‌ها است.")
        return

    session = get_session()
    group_id = update.effective_chat.id

    # Message stats (requires more complex tracking or estimation)
    # For now, let's show members and active users from DB who interacted in this group
    total_tracked_users = session.query(Warning).filter(Warning.group_id == group_id).distinct(Warning.user_id).count()

    members_count = await context.bot.get_chat_member_count(group_id)

    text = (
        f"📊 **آمار گروه {update.effective_chat.title}**\n\n"
        f"👥 تعداد اعضا: {members_count}\n"
        f"🤖 وضعیت ربات: فعال ✅\n"
        f"🛡 امنیت: برقرار 🔐\n"
    )
    await update.effective_message.reply_text(text, parse_mode=None)
    session.close()

async def user_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text == "👤 پروفایل":
        await profile_cmd(update, context)
    elif text == "🏆 رتبه جهانی":
        await rank_cmd(update, context)
    elif text == "📜 سوابق اخطار":
        from bot.modules.warnings import warns_cmd
        await warns_cmd(update, context)
    elif text == "📊 آمار گروه":
        await group_stats_cmd(update, context)

def get_profile_handlers():
    return [
        CommandHandler("profile", profile_cmd),
        CommandHandler("stats", group_stats_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(👤 پروفایل|🏆 رتبه جهانی|📜 سوابق اخطار|📊 آمار گروه)$"), user_button_handler),
        MessageHandler(filters.ALL & ~filters.COMMAND, count_message),
    ]
