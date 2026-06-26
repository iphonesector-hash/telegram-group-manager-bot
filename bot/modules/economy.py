import datetime
import random
import re
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
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

    # Use utcnow if UTC is not available
    try:
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    except AttributeError:
        now = datetime.datetime.utcnow()

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
    coins = user.coins if user else 0
    await update.message.reply_text(f"💰 موجودی کیف پول شما:\n\n{coins} سکه", parse_mode=None)
    session.close()

async def transfer_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ برای انتقال سکه، روی پیام فرد مورد نظر ریپلای کنید و مقدار را بنویسید.\nمثال: /transfer 100", parse_mode=None)
        return

    try:
        amount = int(context.args[0]) if context.args else int(re.search(r'\d+', update.message.text).group())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ مقدار نامعتبر است.")
        return

    from_id = update.effective_user.id
    to_id = update.message.reply_to_message.from_user.id

    if from_id == to_id:
        await update.message.reply_text("❌ نمی‌توانید به خودتان سکه انتقال دهید!")
        return

    session = get_session()
    user_from = session.query(User).filter(User.id == from_id).first()
    user_to = session.query(User).filter(User.id == to_id).first()

    if not user_from or user_from.coins < amount:
        await update.message.reply_text("❌ موجودی کافی نیست.")
        session.close()
        return

    if not user_to:
        await update.message.reply_text("❌ کاربر مقصد در سیستم ثبت نشده است.")
        session.close()
        return

    user_from.coins -= amount
    user_to.coins += amount
    session.commit()
    await update.message.reply_text(f"✅ مبلغ {amount} سکه با موفقیت به {update.message.reply_to_message.from_user.first_name} انتقال یافت.", parse_mode=None)
    session.close()

async def loan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()
    if user:
        loan_amount = 200
        user.coins += loan_amount
        session.commit()
        await update.message.reply_text(f"🏦 مبلغ {loan_amount} سکه وام بانکی به حساب شما واریز شد.\n⚠️ فراموش نکنید که باید آن را بازپرداخت کنید!", parse_mode=None)
    session.close()

async def repay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()
    if user and user.coins >= 200:
        user.coins -= 200
        session.commit()
        await update.message.reply_text("📉 بازپرداخت وام با موفقیت انجام شد. اعتبار بانکی شما افزایش یافت.")
    else:
        await update.message.reply_text("❌ موجودی کافی برای بازپرداخت وام (۲۰۰ سکه) ندارید.")
    session.close()

async def top_coins_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()
    if not top_users:
        await update.message.reply_text("هنوز کسی امتیازی کسب نکرده.")
    else:
        lines = [f"{i+1}. {u.first_name} — 🪙 {u.coins}" for i, u in enumerate(top_users)]
        await update.message.reply_text("🏆 ثروتمندترین‌های سکتور:\n\n" + "\n".join(lines), parse_mode=None)
    session.close()

async def rank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()
    if not user:
        session.close()
        return
    total_users = session.query(User).count()
    rank = session.query(User).filter(User.coins > user.coins).count() + 1
    msg_rank = session.query(User).filter(User.message_count > user.message_count).count() + 1
    text = (
        f"🏆 رتبه شما در SectorBot\n\n"
        f"💰 رتبه ثروت: {rank} از {total_users}\n"
        f"📨 رتبه فعالیت: {msg_rank} از {total_users}\n"
        f"🌟 سطح فعلی: {user.level}"
    )
    await update.message.reply_text(text, parse_mode=None)
    session.close()

async def economy_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "💰 موجودی کیف پول": await coins_cmd(update, context)
    elif text == "🎁 هدیه روزانه": await daily_cmd(update, context)
    elif text == "💸 انتقال سکه": await update.message.reply_text("💸 برای انتقال سکه، روی پیام کاربر مورد نظر ریپلای کرده و دستور /transfer [مقدار] را بزنید.")
    elif text == "🏦 وام بانکی": await loan_cmd(update, context)
    elif text == "📉 بازپرداخت وام": await repay_cmd(update, context)
    elif text == "🏆 برترین‌های ثروت": await top_coins_cmd(update, context)

def get_handlers():
    return [
        CommandHandler("daily", daily_cmd),
        CommandHandler("coins", coins_cmd),
        CommandHandler("transfer", transfer_coins),
        CommandHandler("loan", loan_cmd),
        CommandHandler("repay", repay_cmd),
        CommandHandler("rank", rank_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(💰 موجودی کیف پول|🎁 هدیه روزانه|💸 انتقال سکه|🏦 وام بانکی|📉 بازپرداخت وام|🏆 برترین‌های ثروت)$"), economy_button_handler),
    ]
