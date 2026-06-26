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
        await update.effective_message.reply_text("❌ ابتدا پیامی بفرستید تا حساب شما فعال شود.")
        session.close()
        return

    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

    if user.last_daily_claim and (now - user.last_daily_claim).days < 1:
        time_left = datetime.timedelta(days=1) - (now - user.last_daily_claim)
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        await update.effective_message.reply_text(f"❌ شما هدیه امروز را دریافت کرده‌اید.\n⏳ زمان باقی‌مانده: {hours} ساعت و {minutes} دقیقه")
        session.close()
        return

    reward = 100
    user.coins += reward
    user.last_daily_claim = now
    session.commit()

    await update.effective_message.reply_text(f"✅ هدیه روزانه دریافت شد!\n💰 مبلغ {reward} سکه به کیف پول شما اضافه شد.")
    session.close()

async def coins_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()

    if not user:
        await update.effective_message.reply_text("💰 موجودی شما: 0 سکه")
        session.close()
        return

    await update.effective_message.reply_text(f"💰 موجودی کیف پول شما:\n\n**{user.coins} سکه**", parse_mode="Markdown")
    session.close()

async def transfer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    if not context.args or len(context.args) < 2:
        await update.effective_message.reply_text("💡 مثال: `/transfer آیدی_عددی مبلغ`", parse_mode="Markdown")
        return

    target_id = context.args[0]
    amount = context.args[1]

    if not target_id.isdigit() or not amount.isdigit():
        await update.effective_message.reply_text("❌ مقادیر وارد شده باید عدد باشند.")
        return

    target_id = int(target_id)
    amount = int(amount)

    if amount <= 0:
        await update.effective_message.reply_text("❌ مبلغ باید بیشتر از صفر باشد.")
        return

    session = get_session()
    sender = session.query(User).filter(User.id == update.effective_user.id).first()
    receiver = session.query(User).filter(User.id == target_id).first()

    if not receiver:
        await update.effective_message.reply_text("❌ کاربر مقصد یافت نشد.")
        session.close()
        return

    if sender.coins < amount:
        await update.effective_message.reply_text("❌ موجودی کافی نیست.")
        session.close()
        return

    sender.coins -= amount
    receiver.coins += amount
    session.commit()
    await update.effective_message.reply_text(f"✅ مبلغ {amount} سکه به حساب {receiver.first_name} انتقال یافت.")
    session.close()

async def loan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()

    if user.loan_amount > 0:
        await update.effective_message.reply_text(f"❌ شما در حال حاضر یک وام تسویه نشده به مبلغ {user.loan_amount} سکه دارید.")
        session.close()
        return

    loan_val = 1000
    user.coins += loan_val
    user.loan_amount = loan_val
    user.loan_due_date = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) + datetime.timedelta(days=7)

    session.commit()
    await update.effective_message.reply_text(f"✅ وام فوری SectorBot به مبلغ {loan_val} سکه دریافت شد.\n📅 مهلت بازپرداخت: ۷ روز دیگر.")
    session.close()

async def repay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    session = get_session()
    user = session.query(User).filter(User.id == update.effective_user.id).first()

    if user.loan_amount <= 0:
        await update.effective_message.reply_text("❌ شما هیچ وامی برای بازپرداخت ندارید.")
        session.close()
        return

    if user.coins < user.loan_amount:
        await update.effective_message.reply_text(f"❌ موجودی شما برای بازپرداخت وام ({user.loan_amount} سکه) کافی نیست.")
        session.close()
        return

    user.coins -= user.loan_amount
    user.loan_amount = 0
    user.loan_due_date = None

    session.commit()
    await update.effective_message.reply_text("✅ وام شما با موفقیت تسویه شد. از خوش‌حسابی شما متشکریم!")
    session.close()

async def richest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    try:
        top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()
        if not top_users:
            await update.effective_message.reply_text("هنوز کسی سکه کسب نکرده است.")
            return

        lines = []
        for i, user in enumerate(top_users, start=1):
            name = user.first_name or "نامشخص"
            lines.append(f"{i}. {name} — 💰 {user.coins} سکه")

        await update.effective_message.reply_text("💎 **لیست ثروتمندترین کاربران SectorBot:**\n\n" + "\n".join(lines), parse_mode="Markdown")
    finally:
        session.close()

def get_handlers():
    return [
        CommandHandler("daily", daily_cmd),
        CommandHandler("coins", coins_cmd),
        CommandHandler("transfer", transfer_cmd),
        CommandHandler("loan", loan_cmd),
        CommandHandler("repay", repay_cmd),
        CommandHandler("richest", richest_cmd),
    ]
