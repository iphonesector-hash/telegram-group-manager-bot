from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from bot.modules.locks import locks


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # هم در PV هم در گروه کار می‌کند
    if update.message:
        await update.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)
    else:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, "پنل مدیریت:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # مثل lock_links
    action, lock_type = data.split("_")  # action=lock / unlock, lock_type=links,...

    if lock_type not in locks:
        await query.edit_message_text("❌ قفل نامعتبر است.")
        return

    # تنظیم وضعیت قفل
    locks[lock_type] = (action == "lock")

    if action == "lock":
        await query.edit_message_text(f"🔒 قفل {lock_type} فعال شد")
    else:
        await query.edit_message_text(f"🔓 قفل {lock_type} غیرفعال شد")


def get_panel_handlers():
    return [
        CommandHandler("panel", panel),
        CallbackQueryHandler(button_handler),
    ]
