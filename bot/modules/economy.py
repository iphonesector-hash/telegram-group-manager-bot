import datetime
import re
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import User


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _aware(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


def _get_user(session, update: Update):
    if not update.effective_user:
        return None
    return session.query(User).filter(User.id == update.effective_user.id).first()


async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    user = _get_user(session, update)
    if not user:
        session.close()
        await update.effective_message.reply_text("❌ ابتدا یک پیام در گروه بفرست تا حسابت ساخته شود.")
        raise ApplicationHandlerStop()

    now = _now()
    last_claim = _aware(user.last_daily_claim)
    vip_until = _aware(user.vip_until)
    if last_claim and now - last_claim < datetime.timedelta(hours=24):
        left = datetime.timedelta(hours=24) - (now - last_claim)
        hours, rem = divmod(int(left.total_seconds()), 3600)
        minutes = rem // 60
        session.close()
        await update.effective_message.reply_text(f"⏳ جایزه امروز را گرفتی؛ {hours} ساعت و {minutes} دقیقه دیگه دوباره بیا.")
        raise ApplicationHandlerStop()

    reward = 75 if vip_until and vip_until > now else 50
    user.coins += reward
    user.last_daily_claim = now
    session.commit()
    coins = user.coins
    session.close()
    await update.effective_message.reply_text(f"🎁 جایزه روزانه: +{reward} سکه\n👛 موجودی کیف پول: {coins:,}")
    raise ApplicationHandlerStop()


async def coins_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    user = _get_user(session, update)
    wallet = user.coins if user else 0
    bank = user.bank_balance if user else 0
    loan = user.loan_balance if user else 0
    session.close()
    await update.effective_message.reply_text(
        f"💳 حساب SectorBank\n\n👛 کیف پول: {wallet:,}\n🏦 بانک: {bank:,}\n💎 دارایی: {wallet + bank:,}\n📛 بدهی: {loan:,}"
    )
    raise ApplicationHandlerStop()


async def deposit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except Exception:
        await update.effective_message.reply_text("مثال: /deposit 100")
        raise ApplicationHandlerStop()

    session = get_session(); user = _get_user(session, update)
    if not user or user.coins < amount:
        session.close(); await update.effective_message.reply_text("❌ موجودی کیف پول کافی نیست."); raise ApplicationHandlerStop()
    user.coins -= amount; user.bank_balance += amount; session.commit(); bank = user.bank_balance; session.close()
    await update.effective_message.reply_text(f"✅ {amount:,} سکه به بانک واریز شد.\n🏦 موجودی بانک: {bank:,}")
    raise ApplicationHandlerStop()


async def withdraw_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except Exception:
        await update.effective_message.reply_text("مثال: /withdraw 100")
        raise ApplicationHandlerStop()

    session = get_session(); user = _get_user(session, update)
    if not user or user.bank_balance < amount:
        session.close(); await update.effective_message.reply_text("❌ موجودی بانک کافی نیست."); raise ApplicationHandlerStop()
    user.bank_balance -= amount; user.coins += amount; session.commit(); wallet = user.coins; session.close()
    await update.effective_message.reply_text(f"✅ {amount:,} سکه برداشت شد.\n👛 کیف پول: {wallet:,}")
    raise ApplicationHandlerStop()


async def transfer_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.reply_to_message:
        await update.effective_message.reply_text("روی پیام کاربر ریپلای کن و بزن: /transfer 100")
        raise ApplicationHandlerStop()
    try:
        amount = int(context.args[0]) if context.args else int(re.search(r"\d+", update.effective_message.text or "").group())
        if amount <= 0:
            raise ValueError
    except Exception:
        await update.effective_message.reply_text("❌ مقدار نامعتبر است.")
        raise ApplicationHandlerStop()

    sender_id = update.effective_user.id
    target = update.effective_message.reply_to_message.from_user
    if not target or target.is_bot or target.id == sender_id:
        await update.effective_message.reply_text("❌ مقصد انتقال معتبر نیست.")
        raise ApplicationHandlerStop()

    session = get_session()
    sender = session.query(User).filter(User.id == sender_id).first()
    receiver = session.query(User).filter(User.id == target.id).first()
    if not sender or not receiver or sender.coins < amount:
        session.close(); await update.effective_message.reply_text("❌ موجودی کافی نیست یا کاربر مقصد هنوز ثبت نشده."); raise ApplicationHandlerStop()
    sender.coins -= amount; receiver.coins += amount; session.commit(); left = sender.coins; session.close()
    await update.effective_message.reply_text(f"✅ {amount:,} سکه به {target.first_name} منتقل شد.\n👛 باقی‌مانده: {left:,}")
    raise ApplicationHandlerStop()


async def loan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(context.args[0]) if context.args else 200
    except Exception:
        amount = 200
    if amount < 50 or amount > 500:
        await update.effective_message.reply_text("❌ مقدار وام باید بین ۵۰ تا ۵۰۰ سکه باشد.")
        raise ApplicationHandlerStop()

    session = get_session(); user = _get_user(session, update)
    if not user:
        session.close(); raise ApplicationHandlerStop()
    if user.loan_balance > 0:
        debt = user.loan_balance; session.close(); await update.effective_message.reply_text(f"📛 اول وام قبلی را تسویه کن. بدهی: {debt:,}"); raise ApplicationHandlerStop()
    payback = int(amount * 1.10)
    user.coins += amount; user.loan_balance = payback; session.commit(); session.close()
    await update.effective_message.reply_text(f"🏦 {amount:,} سکه وام گرفتی.\n📛 مبلغ بازپرداخت: {payback:,} سکه")
    raise ApplicationHandlerStop()


async def repay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(); user = _get_user(session, update)
    if not user:
        session.close(); raise ApplicationHandlerStop()
    debt = user.loan_balance
    if debt <= 0:
        session.close(); await update.effective_message.reply_text("✅ وام فعالی نداری."); raise ApplicationHandlerStop()
    if user.coins < debt:
        wallet = user.coins; session.close(); await update.effective_message.reply_text(f"❌ برای تسویه {debt:,} سکه لازم داری. موجودی: {wallet:,}"); raise ApplicationHandlerStop()
    user.coins -= debt; user.loan_balance = 0; session.commit(); session.close()
    await update.effective_message.reply_text("✅ وام کامل تسویه شد.")
    raise ApplicationHandlerStop()


async def top_coins_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(); users = session.query(User).order_by(User.coins.desc()).limit(10).all()
    lines = [f"{i+1}. {u.first_name} — 🪙 {u.coins:,}" for i, u in enumerate(users)]
    session.close(); await update.effective_message.reply_text("🏆 ثروتمندترین‌های سکتور:\n\n" + ("\n".join(lines) if lines else "هنوز کسی ثبت نشده.")); raise ApplicationHandlerStop()


async def rank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(); user = _get_user(session, update)
    if not user:
        session.close(); raise ApplicationHandlerStop()
    total = session.query(User).count(); wealth = session.query(User).filter(User.coins > user.coins).count() + 1; activity = session.query(User).filter(User.message_count > user.message_count).count() + 1
    session.close(); await update.effective_message.reply_text(f"🏆 رتبه شما\n\n💰 ثروت: {wealth} از {total}\n📨 فعالیت: {activity} از {total}\n🌟 لول: {user.level}"); raise ApplicationHandlerStop()


async def economy_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text in ("💰 موجودی کیف پول", "💰 موجودی سکه"): await coins_cmd(update, context)
    elif text == "🎁 هدیه روزانه": await daily_cmd(update, context)
    elif text == "💸 انتقال سکه": await update.effective_message.reply_text("روی پیام کاربر ریپلای کن و بزن: /transfer 100")
    elif text == "🏦 وام بانکی": await loan_cmd(update, context)
    elif text == "📉 بازپرداخت وام": await repay_cmd(update, context)
    elif text == "🏆 برترین‌های ثروت": await top_coins_cmd(update, context)
    elif text == "🔙 بازگشت به منوی اصلی":
        from bot.utils.keyboards import get_main_menu
        await update.effective_message.reply_text("🏠 منوی اصلی:", reply_markup=get_main_menu())
    raise ApplicationHandlerStop()


def get_handlers():
    return [
        CommandHandler("daily", daily_cmd), CommandHandler("coins", coins_cmd),
        CommandHandler("deposit", deposit_cmd), CommandHandler("withdraw", withdraw_cmd),
        CommandHandler("transfer", transfer_coins), CommandHandler("loan", loan_cmd),
        CommandHandler("repay", repay_cmd), CommandHandler("payloan", repay_cmd),
        CommandHandler("rank", rank_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(💰 موجودی کیف پول|💰 موجودی سکه|🎁 هدیه روزانه|💸 انتقال سکه|🏦 وام بانکی|📉 بازپرداخت وام|🏆 برترین‌های ثروت|🔙 بازگشت به منوی اصلی)$"), economy_button_handler),
    ]
