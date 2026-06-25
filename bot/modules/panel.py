from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from bot.database.session import get_session
from bot.database.models import Group

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("این دستور فقط در گروه‌ها کاربرد دارد.")
        return

    keyboard = [
        [
            InlineKeyboardButton("🔒 قفل لینک‌ها", callback_data="lock_links"),
            InlineKeyboardButton("🔓 باز کردن لینک‌ها", callback_data="unlock_links"),
        ],
        [
            InlineKeyboardButton("🔒 قفل عکس‌ها", callback_data="lock_photos"),
            InlineKeyboardButton("🔓 باز کردن عکس‌ها", callback_data="unlock_photos"),
        ],
        [
            InlineKeyboardButton("🔒 قفل ویدیو", callback_data="lock_videos"),
            InlineKeyboardButton("🔓 باز کردن ویدیو", callback_data="unlock_videos"),
        ],
        [
            InlineKeyboardButton("🔒 قفل استیکر", callback_data="lock_stickers"),
            InlineKeyboardButton("🔓 باز کردن استیکر", callback_data="unlock_stickers"),
        ],
        [
            InlineKeyboardButton("🔒 قفل فوروارد", callback_data="lock_forward"),
            InlineKeyboardButton("🔓 باز کردن فوروارد", callback_data="unlock_forward"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("پنل مدیریت گروه:", reply_markup=reply_markup)
    else:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, "پنل مدیریت گروه:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, lock_type = data.split("_")

    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()

    if not group:
        await query.edit_message_text("❌ گروه در پایگاه داده یافت نشد.")
        session.close()
        return

    attr = f"lock_{lock_type}"
    if not hasattr(group, attr):
        await query.edit_message_text("❌ قفل نامعتبر است.")
        session.close()
        return

    setattr(group, attr, (action == "lock"))
    session.commit()

    status = "فعال" if action == "lock" else "غیرفعال"
    icon = "🔒" if action == "lock" else "🔓"
    await query.edit_message_text(f"{icon} قفل {lock_type} {status} شد.")
    session.close()


def get_panel_handlers():
    return [
        CommandHandler("panel", panel),
        CallbackQueryHandler(button_handler),
    ]
