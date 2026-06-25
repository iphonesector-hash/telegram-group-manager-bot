import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.database.session import get_session
from bot.database.models import User, Group

async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()

    if not user:
        await update.message.reply_text("❌ ابتدا پیامی بفرستید تا حساب شما فعال شود.")
        session.close()
        return

    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

    if user.last_daily_claim and (now - user.last_daily_claim).days < 1:
        time_left = datetime.timedelta(days=1) - (now - user.last_daily_claim)
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        await update.message.reply_text(f"❌ شما هدیه امروز را دریافت کرده‌اید.\n⏳ زمان باقی‌مانده: {hours} ساعت و {minutes} دقیقه")
        session.close()
        return

    reward = 50
    user.coins += reward
    user.last_daily_claim = now
    session.commit()

    await update.message.reply_text(f"✅ هدیه روزانه دریافت شد!\n💰 مبلغ {reward} سکه به کیف پول شما اضافه شد.")
    session.close()

async def coins_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()

    if not user:
        await update.message.reply_text("💰 موجودی شما: 0 سکه")
        session.close()
        return

    await update.message.reply_text(f"💰 موجودی کیف پول شما:\n\n**{user.coins} سکه**", parse_mode="Markdown")
    session.close()

async def rank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()

    if not user:
        session.close()
        return

    # Global rank by coins
    total_users = session.query(User).count()
    rank = session.query(User).filter(User.coins > user.coins).count() + 1

    # Activity rank by message count
    msg_rank = session.query(User).filter(User.message_count > user.message_count).count() + 1

    text = (
        f"🏆 **رتبه شما در SectorBot**\n\n"
        f"💰 رتبه ثروت: {rank} از {total_users}\n"
        f"📨 رتبه فعالیت: {msg_rank} از {total_users}\n"
        f"🌟 سطح فعلی: {user.level}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    session.close()

def get_handlers():
    return [
        CommandHandler("daily", daily_cmd),
        CommandHandler("coins", coins_cmd),
        CommandHandler("rank", rank_cmd),
    ]
