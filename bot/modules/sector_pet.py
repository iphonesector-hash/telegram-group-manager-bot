import os
import datetime
import random
import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUsers, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, ApplicationHandlerStop, filters

from bot.database.session import get_session
from bot.database.models import AppSetting, Purchase, User
from bot.modules.ai import get_ai_response, get_sector_prompt
from bot.services import sector_pet as service


MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0] + "?v=20260823-3"


def sector_emoji_id():
    try:session=get_session()
    except RuntimeError:return None
    try:
        row=session.query(AppSetting).filter(AppSetting.key=="sector_custom_emoji_id").first()
        return str(row.value) if row and row.value else None
    finally:session.close()


def pet_keyboard():
    icon=sector_emoji_id()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("شارژ", callback_data="sector_action:charge",style="success",icon_custom_emoji_id=icon), InlineKeyboardButton("بازی", callback_data="sector_action:play",style="primary")],
        [InlineKeyboardButton("تمرین", callback_data="sector_action:train",style="primary"), InlineKeyboardButton("یادگیری", callback_data="sector_action:learn",style="success")],
        [InlineKeyboardButton("تعمیر", callback_data="sector_action:repair",style="danger"), InlineKeyboardButton("تازه‌سازی", callback_data="sector_pet",style="primary")],
        [InlineKeyboardButton("ماموریت و چالش",callback_data="sector_quests",style="success"),InlineKeyboardButton("مهارت‌ها",callback_data="sector_skills",style="primary")],
        [InlineKeyboardButton("مسیر تکامل",callback_data="sector_evolution",style="primary"),InlineKeyboardButton("گالری سکتور",callback_data="sector_art",style="success")],
        [InlineKeyboardButton("حرف‌زدن و تعامل‌ها", callback_data="sector_social",style="primary",icon_custom_emoji_id=icon)],
        [InlineKeyboardButton("نسخه کامل در مینی‌اپ", web_app=WebAppInfo(url=MINI_APP_URL),style="success")],
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


def social_keyboard():
    icon=sector_emoji_id()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تغییر نام",callback_data="sector_ui:rename",style="primary",icon_custom_emoji_id=icon),InlineKeyboardButton("گفت‌وگو",callback_data="sector_ui:talk",style="success")],
        [InlineKeyboardButton("بازی دونفره",callback_data="sector_ui:play",style="primary"),InlineKeyboardButton("عملیات بانکی",callback_data="sector_ui:rob",style="danger")],
        [InlineKeyboardButton("بازگشت به سکتور",callback_data="sector_pet",style="primary")],
    ])


def back_keyboard(extra=None):
    rows=extra or []
    return InlineKeyboardMarkup(rows+[[InlineKeyboardButton("بازگشت به سکتور",callback_data="sector_pet",style="primary")]])


def quest_text(pet,daily,claimed=False):
    return (f"🎯 <b>ماموریت‌های {html.escape(pet['name'])}</b>\n\n"
            f"{'✅' if daily['complete'] else '🔄'} مراقبت روزانه: {min(daily['actions'],3)}/3\n"
            f"🔥 حفظ زنجیره حضور: {pet['streak_days']} روز\n"
            f"🧠 دانش‌آموز سکتور: دانش {pet['knowledge']}/100\n"
            f"💙 حال خوب: شادی {pet['happiness']}/100\n\n"
            f"🎁 جایزه مراقبت: ۸۰ سکه + ۳۵ XP\n"
            f"وضعیت جایزه: {'دریافت شده' if claimed else ('آماده دریافت' if daily['complete'] else 'هنوز کامل نشده')}")


def user_picker(action):
    request_id=9101 if action=="play" else 9102
    title="یک دوست برای بازی انتخاب کن" if action=="play" else "هدف عملیات را انتخاب کن"
    return title,ReplyKeyboardMarkup([[KeyboardButton("انتخاب کاربر",request_users=KeyboardButtonRequestUsers(request_id=request_id,user_is_bot=False,max_quantity=1))],[KeyboardButton("لغو عملیات",style="danger")]],resize_keyboard=True,one_time_keyboard=True)


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
            await query.edit_message_text("🤝 <b>تعامل‌های سکتور</b>\n\nهمه امکانات را از دکمه‌های زیر اجرا کن.",parse_mode="HTML",reply_markup=social_keyboard())
            return
        if query.data in ("sector_quests","sector_skills","sector_evolution","sector_art","sector_claim_daily"):
            await query.answer();pet,daily=load_pet(query.from_user.id)
            if query.data=="sector_art":
                await query.message.reply_photo("https://isectorland-miniapp.vercel.app/assets/sector-evolution.webp",caption="🎨 چهار نسل فعلی سکتور؛ نسل‌ها و حالت‌های انیمیشنی بیشتری در حال اضافه‌شدن است.",reply_markup=back_keyboard())
                return
            if query.data=="sector_skills":
                unlocked=["گفت‌وگوی صمیمی","بازی و مراقبت"]
                if pet['level']>=10:unlocked+=['تحلیل و یادگیری سریع','شانس بیشتر در عملیات']
                if pet['level']>=30:unlocked+=['ماموریت‌های حرفه‌ای','پاداش تیمی']
                if pet['level']>=60:unlocked+=['فرم همه‌چیزدان','توانایی‌های ویژه']
                await query.edit_message_text("🧠 <b>مهارت‌های سکتور</b>\n\n"+"\n".join("✅ "+x for x in unlocked)+"\n\nمهارت بعدی با بالا رفتن سطح و روزهای مراقبت آزاد می‌شود.",parse_mode="HTML",reply_markup=back_keyboard());return
            if query.data=="sector_evolution":
                await query.edit_message_text("🧬 <b>مسیر تکامل چندماهه</b>\n\n🤖 کوچولو — شروع\n🔹 کنجکاو — سطح ۱۰ + ۱۴ روز\n⚙️ حرفه‌ای — سطح ۳۰ + ۶۰ روز\n👑 همه‌چیزدان — سطح ۶۰ + ۱۵۰ روز\n\nدر آینده شاخه‌های شخصیتی و فرم‌های کمیاب نیز به این مسیر اضافه می‌شوند.",parse_mode="HTML",reply_markup=back_keyboard());return
            session=get_session()
            try:
                key=f"sector_daily:{query.from_user.id}:{datetime.datetime.utcnow().strftime('%Y%m%d')}";claimed=session.query(Purchase.id).filter(Purchase.telegram_payment_charge_id==key).first() is not None
                if query.data=="sector_claim_daily" and daily['complete'] and not claimed:
                    user=session.query(User).filter(User.id==query.from_user.id).with_for_update().first();pet_obj=service.get_or_create_pet(session,query.from_user.id,lock=True)
                    user.coins=int(user.coins or 0)+80;pet_obj.xp=int(pet_obj.xp or 0)+35;session.add(Purchase(user_id=user.id,item_id="sector_daily_reward",amount=80,status="reward",telegram_payment_charge_id=key));session.commit();claimed=True;pet=service.serialize_pet(pet_obj)
                buttons=[] if claimed else [[InlineKeyboardButton("دریافت جایزه",callback_data="sector_claim_daily",style="success")]]
                await query.edit_message_text(quest_text(pet,daily,claimed),parse_mode="HTML",reply_markup=back_keyboard(buttons))
            finally:session.close()
            return
        if query.data.startswith("sector_ui:"):
            action=query.data.split(":",1)[1];await query.answer()
            if action in ("rename","talk"):
                context.user_data["sector_pending"]=action
                prompt="اسم جدید سکتورت را بفرست:" if action=="rename" else "پیامت را برای سکتور بنویس:"
                await query.message.reply_text(prompt,reply_markup=ReplyKeyboardMarkup([[KeyboardButton("لغو عملیات",style="danger")]],resize_keyboard=True,one_time_keyboard=True))
            else:
                context.user_data["sector_pending"]=action
                title,markup=user_picker(action);await query.message.reply_text(title,reply_markup=markup)
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


async def set_sector_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 5147526780:
        raise ApplicationHandlerStop()
    source=update.effective_message.reply_to_message or update.effective_message
    entities=list(source.entities or [])+list(source.caption_entities or [])
    custom_id=next((e.custom_emoji_id for e in entities if str(e.type)=="custom_emoji" and e.custom_emoji_id),None)
    if not custom_id:
        await update.effective_message.reply_text("یک پیام حاوی ایموجی متحرک پرمیوم بفرست، روی آن ریپلای کن و /setsectoremoji را بزن.")
        raise ApplicationHandlerStop()
    session=get_session()
    try:
        row=session.query(AppSetting).filter(AppSetting.key=="sector_custom_emoji_id").first()
        if row:row.value=custom_id
        else:session.add(AppSetting(key="sector_custom_emoji_id",value=custom_id))
        session.commit()
    finally:session.close()
    await update.effective_message.reply_text("✅ ایموجی متحرک سکتور روی دکمه‌های اختصاصی فعال شد.")
    raise ApplicationHandlerStop()


async def capture_sector_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner can simply send a Premium custom emoji once to configure Sector."""
    await set_sector_emoji(update,context)


async def pending_text(update:Update,context:ContextTypes.DEFAULT_TYPE):
    action=context.user_data.get("sector_pending")
    if not action:return
    text=(update.effective_message.text or "").strip()
    if text=="لغو عملیات":
        context.user_data.pop("sector_pending",None);await update.effective_message.reply_text("عملیات لغو شد.",reply_markup=ReplyKeyboardRemove());raise ApplicationHandlerStop()
    if action=="rename":
        context.args=[text];context.user_data.pop("sector_pending",None);await update.effective_message.reply_text("نام دریافت شد.",reply_markup=ReplyKeyboardRemove());await sector_name(update,context)
    elif action=="talk":
        context.args=[text];context.user_data.pop("sector_pending",None);await update.effective_message.reply_text("سکتور در حال فکرکردن است…",reply_markup=ReplyKeyboardRemove());await sector_talk(update,context)


async def selected_user(update:Update,context:ContextTypes.DEFAULT_TYPE):
    shared=update.effective_message.users_shared
    action=context.user_data.pop("sector_pending",None)
    if not shared or action not in ("play","rob") or not shared.users:return
    target_id=shared.users[0].user_id
    if target_id==update.effective_user.id:
        await update.effective_message.reply_text("خودت را نمی‌توانی انتخاب کنی.",reply_markup=ReplyKeyboardRemove());raise ApplicationHandlerStop()
    session=get_session()
    try: target=session.query(User).filter(User.id==target_id).first();target_name=target.first_name if target else f"کاربر {target_id}"
    finally:session.close()
    context.user_data["sector_selected_target"]={"id":target_id,"name":target_name}
    await update.effective_message.reply_text(f"✅ {target_name} انتخاب شد.",reply_markup=ReplyKeyboardRemove())
    await run_selected_action(update,context,action,target_id,target_name)


async def run_selected_action(update,context,action,target_id,target_name):
    attacker_id=update.effective_user.id
    if action=="play":
        dice=await update.effective_message.reply_dice(emoji="🎲");session=get_session()
        try:
            for uid in (attacker_id,target_id):
                if not session.query(User.id).filter(User.id==uid).first():continue
                pet=service.get_or_create_pet(session,uid,lock=True);service.touch_daily_visit(pet);pet.happiness=min(100,int(pet.happiness or 0)+8);pet.xp=int(pet.xp or 0)+5
            session.commit()
        finally:session.close()
        await update.effective_message.reply_text(f"🎉 بازی با {target_name} انجام شد؛ تاس {dice.dice.value} و هر سکتور +۵ XP گرفت.")
    else:
        await execute_robbery(update,attacker_id,target_id,target_name)
    raise ApplicationHandlerStop()


async def execute_robbery(update,attacker_id,target_id,target_name):
    slot=await update.effective_message.reply_dice(emoji="🎰");session=get_session()
    try:
        now=datetime.datetime.utcnow();start=now.replace(hour=0,minute=0,second=0,microsecond=0)
        attempts=session.query(Purchase).filter(Purchase.user_id==attacker_id,Purchase.item_id=="sector_rob_attempt",Purchase.created_at>=start).count()
        attacker=session.query(User).filter(User.id==attacker_id).with_for_update().first();victim=session.query(User).filter(User.id==target_id).with_for_update().first()
        if attempts>=3:message="⏳ سهمیه سه عملیات امروزت تمام شده."
        elif not attacker or not victim:message="هر دو کاربر باید قبلاً /start را زده باشند."
        elif int(attacker.coins or 0)<25:message="برای عملیات ۲۵ سکه لازم داری."
        else:
            attacker.coins=int(attacker.coins or 0)-25;ap=service.get_or_create_pet(session,attacker_id);vp=service.get_or_create_pet(session,target_id)
            chance=max(18,min(45,28+(int(ap.knowledge or 0)-int(vp.knowledge or 0))//10));success=random.randint(1,100)<=chance and int(victim.bank_balance or 0)>0
            amount=min(500,max(1,int(victim.bank_balance or 0)*2//100)) if success else 0
            if success:victim.bank_balance=int(victim.bank_balance or 0)-amount;attacker.coins+=amount;ap.xp=int(ap.xp or 0)+12
            session.add(Purchase(user_id=attacker_id,item_id="sector_rob_attempt",amount=amount,status="success" if success else "failed",telegram_payment_charge_id=f"sectorrob:{attacker_id}:{target_id}:{now.timestamp()}"));session.commit()
            message=(f"🎰 عملیات موفق شد؛ {amount} سکه از بانک {target_name} گرفتی!" if success else "🚨 عملیات لو رفت و ۲۵ سکه هزینه از دست رفت.")+f"\nنتیجه: {slot.dice.value} • شانس: {chance}٪"
        await update.effective_message.reply_text(message)
    finally:session.close()


def get_handlers():
    return [CommandHandler("sector", sector_command),CommandHandler("sectorname",sector_name),CommandHandler("sectortalk",sector_talk),CommandHandler("sectorplay",sector_play),CommandHandler("sectorrob",sector_rob),CommandHandler("setsectoremoji",set_sector_emoji),MessageHandler(filters.User(5147526780)&filters.Entity("custom_emoji"),capture_sector_emoji),MessageHandler(filters.StatusUpdate.USERS_SHARED,selected_user),MessageHandler(filters.TEXT&~filters.COMMAND,pending_text),CallbackQueryHandler(sector_callback, pattern=r"^sector_(pet|action:|social|ui:|quests|skills|evolution|art|claim_daily)")]
