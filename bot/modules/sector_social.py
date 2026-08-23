import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ApplicationHandlerStop, CallbackQueryHandler, CommandHandler, ContextTypes

from bot.database.models import User
from bot.database.session import get_session
from bot.services import sector_pet as service
from bot.services.sector_economy import appearance_icons

MINI_APP_URL = "https://isectorland-miniapp.vercel.app"


def _reply_target(update: Update):
    message = update.effective_message
    reply = message.reply_to_message if message else None
    user = reply.from_user if reply and reply.from_user else None
    if not user or user.is_bot or user.id == update.effective_user.id:
        return None
    return user


def _gear_line(pet):
    items = appearance_icons(pet)
    if not items:
        return "بدون تجهیزات"
    return " ".join(item["icon"] for item in items) + "  " + " • ".join(item["title"] for item in items[:4])


def _action_keyboard(actor_id, target_id):
    prefix = f"sectorx:{actor_id}:{target_id}:"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚔️ دوئل", callback_data=prefix + "battle", style="danger"),
            InlineKeyboardButton("🎁 هدیه ۵۰", callback_data=prefix + "gift", style="success"),
        ],
        [
            InlineKeyboardButton("🏠 ملاقات", callback_data=prefix + "visit", style="primary"),
            InlineKeyboardButton("🐾 کارت سکتور", callback_data=prefix + "profile", style="primary"),
        ],
        [InlineKeyboardButton("sector", web_app=WebAppInfo(url=MINI_APP_URL))],
    ])


def _card(actor_user, actor_pet, target_user, target_pet):
    return (
        "🐾 <b>تعامل سکتورها</b>\n\n"
        f"🤖 <b>{html.escape(actor_pet.name)}</b> • {html.escape(actor_user.first_name or 'کاربر')} • Lv.{service.level_from_xp(actor_pet.xp)}\n"
        f"👕 {_gear_line(actor_pet)}\n\n"
        "VS / WITH\n\n"
        f"🤖 <b>{html.escape(target_pet.name)}</b> • {html.escape(target_user.first_name or 'کاربر')} • Lv.{service.level_from_xp(target_pet.xp)}\n"
        f"👕 {_gear_line(target_pet)}\n\n"
        "یک اکشن انتخاب کن؛ همین کارت به‌روزرسانی می‌شود تا تاپیک شلوغ نشود."
    )


async def show_sector_reply_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, target=None):
    if not update.effective_chat or update.effective_chat.type == "private":
        return False
    target = target or _reply_target(update)
    if not target:
        return False
    session = get_session()
    try:
        actor = session.query(User).filter(User.id == update.effective_user.id).first()
        target_db = session.query(User).filter(User.id == target.id).first()
        if not actor or not target_db:
            await update.effective_message.reply_text("🐾 هر دو کاربر باید یک‌بار ربات را /start کرده باشند.")
            return True
        actor_pet = service.get_or_create_pet(session, actor.id)
        target_pet = service.get_or_create_pet(session, target_db.id)
        session.commit()
        await update.effective_message.reply_text(
            _card(actor, actor_pet, target_db, target_pet),
            parse_mode="HTML",
            reply_markup=_action_keyboard(actor.id, target_db.id),
        )
        return True
    finally:
        session.close()


async def sector_actions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text("🐾 این دستور داخل گروه و روی Reply یک کاربر استفاده می‌شود.")
        raise ApplicationHandlerStop()
    if not await show_sector_reply_actions(update, context):
        await update.effective_message.reply_text("🐾 روی پیام یک کاربر Reply کن و /sectoractions بزن.")
    raise ApplicationHandlerStop()


async def sector_social_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        _, actor_raw, target_raw, action = query.data.split(":", 3)
        actor_id, target_id = int(actor_raw), int(target_raw)
    except Exception:
        await query.answer("اکشن نامعتبر است.", show_alert=True)
        return
    if query.from_user.id != actor_id:
        await query.answer("این پنل برای صاحب سکتوریه که اکشن رو شروع کرده.", show_alert=True)
        return

    session = get_session()
    try:
        actor = session.query(User).filter(User.id == actor_id).first()
        target = session.query(User).filter(User.id == target_id).first()
        if not actor or not target:
            await query.answer("یکی از حساب‌ها پیدا نشد.", show_alert=True)
            return
        actor_pet = service.get_or_create_pet(session, actor_id)
        target_pet = service.get_or_create_pet(session, target_id)

        if action == "profile":
            session.commit()
            text = (
                f"🐾 <b>کارت {html.escape(target_pet.name)}</b>\n\n"
                f"👤 صاحب: {html.escape(target.first_name or 'کاربر')}\n"
                f"⭐ سطح: {service.level_from_xp(target_pet.xp)}\n"
                f"🔥 Streak: {int(target_pet.streak_days or 0)} روز\n"
                f"🧠 دانش: {int(target_pet.knowledge or 0)}٪\n"
                f"❤️ سلامت: {int(target_pet.health or 0)}٪\n"
                f"👕 تجهیزات: {_gear_line(target_pet)}"
            )
            await query.answer()
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=_action_keyboard(actor_id, target_id))
            return

        result = service.social_action(session, actor_id, target_id, action)
        if result.get("status") != "success":
            session.rollback()
            await query.answer(result.get("message") or "اکشن انجام نشد.", show_alert=True)
            return
        session.commit()
        actor_pet = service.get_or_create_pet(session, actor_id)
        target_pet = service.get_or_create_pet(session, target_id)
        result_text = f"{_card(actor, actor_pet, target, target_pet)}\n\n━━━━━━━━━━\n<b>{html.escape(result['message'])}</b>"
        await query.answer("انجام شد 🐾")
        await query.edit_message_text(result_text, parse_mode="HTML", reply_markup=_action_keyboard(actor_id, target_id))
    finally:
        session.close()


def get_handlers():
    return [
        CommandHandler("sectoractions", sector_actions_command),
        CallbackQueryHandler(sector_social_callback, pattern=r"^sectorx:\d+:\d+:(battle|gift|visit|profile)$"),
    ]
