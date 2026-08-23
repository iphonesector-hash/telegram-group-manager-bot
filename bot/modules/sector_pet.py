import os
import datetime
import random
import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ApplicationHandlerStop

from bot.database.session import get_session
from bot.database.models import Purchase, User
from bot.modules.ai import get_ai_response, get_sector_prompt
from bot.services import sector_pet as service


MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app")


def pet_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ شارژ", callback_data="sector_action:charge"), InlineKeyboardButton("🎮 بازی", callback_data="sector_action:play")],
        [InlineKeyboardButton("🏋️ تمرین", callback_data="sector_action:train"), InlineKeyboardButton("🧠 یادگیری", callback_data="sector_action:learn")],
        [InlineKeyboardButton("🔧 تعمیر", callback_data="sector_action:repair"), InlineKeyboardButton("🔄 تازه‌سازی", callback_data="sector_pet")],
        [InlineKeyboardButton("💬 حرف‌زدن و تعامل‌ها", callback_data="sector_social")],
        [InlineKeyboardButton("🚀 نسخه کامل در مینی‌اپ", web_app=WebAppInfo(url=MINI_APP_URL))],
    ])


def progress_bar(value, size=10):
    filled = max(0, min(size, round(int(value or 0) / 100 * size)))
    return "▰" * filled + "▱" * (size - filled)


def pet_text(pet, daily):
    gate = (pet.get("stage") or {}).get("next_gate")
    gate_text = "به آخرین فرم رسیده‌ای" if not gate else f"فرم بعدی: سطح {gate['level']} + {gate['care_days']} روز مراقبت"
    return (
        f"🤖 <b>{html.escape(pet['name'])}</b> — {pet['stage']['title']} — سطح {pet['level']}\n\n"
        f"⚡ انرژی   {progress_bar(pet['energy'])} {pet['energy']}٪\n"
        f"💙 شادی    {progress_bar(pet['happiness'])} {pet['happiness']}٪\n"
        f"🧠 دانش    {progress_bar(pet['knowledge'])} {pet['knowledge']}٪\n"
        f"❤️ سلامت  {progress_bar(pet['health'])} {pet['health']}٪\n\n"
        f"🔥 زنجیره حضور: <b>{pet['streak_days']} روز</b>\n"
        f"📅 روزهای مراقبت: <b>{pet['total_care_days']}</b>\n"
        f"🎯 مأموریت امروز: <b>{min(daily['actions'], daily['target'])}/{daily['target']}</b> فعالیت\n"
        f"🧬 {gate_text}\n\n"
        "رشد سکتور با روزهای فعال واقعی انجام می‌شود؛ مراقبت زیاد در یک روز جای بازگشت روزانه را نمی‌گیرد."
    )


SOCIAL_HELP = (
    "🤝 <b>تعامل‌های سکتور</b>\n\n"
    "✏️ تغییر نام: <code>/sectorname نام جدید</code>\n"
    "💬 حرف‌زدن: <code>/sectortalk حالت چطوره؟</code>\n"
    "🎲 بازی دونفره: روی پیام دوستت ریپلای کن و <code>/sectorplay</code> بزن.\n"
    "🏦 عملیات بانکی: روی پیام دوستت ریپلای کن و <code>/sectorrob</code> بزن.\n\n"
    "هر عملیات بانکی شانس موفقیت، هزینه و محدودیت روزانه دارد و فقط بخش کوچکی از موجودی بانک را جابه‌جا می‌کند."
)


def load_pet(user_id):
    session = get_session()
    try:
        pet = service.get_or_create_pet(session, user_id)
        service.refresh_pet(pet)
        service.touch_daily_visit(pet)
        data, daily = service.serialize_pet(pet), service.daily_progress(session, user_id)
        session.commit()
        return data, daily
    finally:
        session.close()


async def sector_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.effective_message.reply_text("🤖 سکتور کوچولو فقط در چت خصوصی رشد می‌کند.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("باز کردن چت خصوصی", url="https://t.me/iSectorlandbot?start=sector")]]))
    else:
        pet, daily = load_pet(update.effective_user.id)
        await update.effective_message.reply_text(pet_text(pet, daily), parse_mode="HTML", reply_markup=pet_keyboard())
    raise ApplicationHandlerStop()


async def sector_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    session = get_session()
    try:
        if query.data == "sector_social":
            await query.answer()
            await query.message.reply_text(SOCIAL_HELP, parse_mode="HTML")
            return
        if query.data.startswith("sector_action:"):
            result = service.perform_action(session, query.from_user.id, query.data.split(":", 1)[1])
            if result["status"] != "success":
                session.rollback()
                await query.answer(result["message"], show_alert=True)
                return
            session.commit()
            pet, daily = result["pet"], result["daily"]
        else:
            pet_obj = service.get_or_create_pet(session, query.from_user.id)
            service.refresh_pet(pet_obj); service.touch_daily_visit(pet_obj)
            pet, daily = service.serialize_pet(pet_obj), service.daily_progress(session, query.from_user.id)
            session.commit()
        await query.answer("انجام شد 🤖" if query.data.startswith("sector_action:") else "به‌روز شد")
        await query.edit_message_text(pet_text(pet, daily), parse_mode="HTML", reply_markup=pet_keyboard())
    finally:
        session.close()


async def sector_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args).strip()
    if not name or len(name) > 20:
        await update.effective_message.reply_text("✏️ نمونه: /sectorname آذرخش\nنام باید حداکثر ۲۰ نویسه باشد.")
        raise ApplicationHandlerStop()
    session = get_session()
    try:
        pet = service.get_or_create_pet(session, update.effective_user.id, lock=True)
        pet.name = name
        session.commit()
        await update.effective_message.reply_text(f"🤖 از حالا اسم همراهت «{name}» است.")
    finally: session.close()
    raise ApplicationHandlerStop()


async def sector_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = " ".join(context.args).strip()
    if not message:
        await update.effective_message.reply_text("💬 نمونه: /sectortalk امروز حالت چطوره؟")
        raise ApplicationHandlerStop()
    pet, _ = load_pet(update.effective_user.id)
    prompt = get_sector_prompt(update.effective_user) + f" نام همراه شخصی کاربر {pet['name']} است. مثل یک ربات کوچولوی دوست‌داشتنی، صمیمی و کوتاه جواب بده. سطح {pet['level']}، شادی {pet['happiness']} و دانش {pet['knowledge']} است."
    answer = await get_ai_response(prompt, message[:700])
    await update.effective_message.reply_text(f"🤖 {pet['name']}:\n{answer or 'الان یکم خواب‌آلودم؛ دوباره صدایم کن!'}")
    raise ApplicationHandlerStop()


def reply_target(update):
    reply = update.effective_message.reply_to_message
    return reply.from_user if reply and reply.from_user and not reply.from_user.is_bot else None


async def sector_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = reply_target(update)
    if not target or target.id == update.effective_user.id:
        await update.effective_message.reply_text("🎲 روی پیام یک کاربر دیگر ریپلای کن و /sectorplay بزن.")
        raise ApplicationHandlerStop()
    dice = await update.effective_message.reply_dice(emoji="🎲")
    session = get_session()
    try:
        names=[]
        for uid in (update.effective_user.id, target.id):
            if not session.query(User.id).filter(User.id == uid).first(): continue
            pet=service.get_or_create_pet(session,uid,lock=True);service.touch_daily_visit(pet)
            pet.happiness=min(100,int(pet.happiness or 0)+8);pet.xp=int(pet.xp or 0)+5
            names.append(pet.name)
        session.commit()
        await update.effective_message.reply_text(f"🎉 {update.effective_user.first_name} و {target.first_name} با سکتورهایشان بازی کردند! تاس: {dice.dice.value} — هر همراه +۵ XP و +۸ شادی گرفت.")
    finally: session.close()
    raise ApplicationHandlerStop()


async def sector_rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = reply_target(update); attacker_id=update.effective_user.id
    if not target or target.id == attacker_id:
        await update.effective_message.reply_text("🏦 روی پیام یک کاربر دیگر ریپلای کن و /sectorrob بزن.")
        raise ApplicationHandlerStop()
    slot = await update.effective_message.reply_dice(emoji="🎰")
    session=get_session()
    try:
        now=datetime.datetime.utcnow();start=now.replace(hour=0,minute=0,second=0,microsecond=0)
        attempts=session.query(Purchase).filter(Purchase.user_id==attacker_id,Purchase.item_id=="sector_rob_attempt",Purchase.created_at>=start).count()
        if attempts>=3:
            await update.effective_message.reply_text("⏳ سهمیه سه عملیات امروزت تمام شده؛ فردا دوباره برگرد.");raise ApplicationHandlerStop()
        attacker=session.query(User).filter(User.id==attacker_id).with_for_update().first();victim=session.query(User).filter(User.id==target.id).with_for_update().first()
        if not attacker or not victim:
            await update.effective_message.reply_text("هر دو کاربر باید قبلاً /start را زده باشند.");raise ApplicationHandlerStop()
        fee=25
        if int(attacker.coins or 0)<fee:
            await update.effective_message.reply_text("برای شروع عملیات ۲۵ سکه لازم داری.");raise ApplicationHandlerStop()
        attacker.coins=int(attacker.coins or 0)-fee
        ap=service.get_or_create_pet(session,attacker_id);vp=service.get_or_create_pet(session,target.id)
        chance=max(18,min(45,28+(int(ap.knowledge or 0)-int(vp.knowledge or 0))//10))
        success=random.randint(1,100)<=chance and int(victim.bank_balance or 0)>0
        amount=min(500,max(1,int(victim.bank_balance or 0)*2//100)) if success else 0
        if success:
            victim.bank_balance=int(victim.bank_balance or 0)-amount;attacker.coins+=amount;ap.xp=int(ap.xp or 0)+12
        session.add(Purchase(user_id=attacker_id,item_id="sector_rob_attempt",amount=amount,status="success" if success else "failed",telegram_payment_charge_id=f"sectorrob:{attacker_id}:{target.id}:{now.timestamp()}"))
        session.commit()
        if success: text=f"🎰 عملیات موفق شد! {ap.name} با نتیجه {slot.dice.value}، {amount} سکه از بانک {target.first_name} برداشت کرد."
        else: text=f"🚨 عملیات لو رفت! نتیجه دستگاه {slot.dice.value} بود و ۲۵ سکه هزینه عملیات از دست رفت."
        await update.effective_message.reply_text(text+f"\nشانس این تلاش: {chance}٪")
    finally: session.close()
    raise ApplicationHandlerStop()


def get_handlers():
    return [CommandHandler("sector", sector_command),CommandHandler("sectorname",sector_name),CommandHandler("sectortalk",sector_talk),CommandHandler("sectorplay",sector_play),CommandHandler("sectorrob",sector_rob),CallbackQueryHandler(sector_callback, pattern=r"^sector_(pet|action:|social)")]
