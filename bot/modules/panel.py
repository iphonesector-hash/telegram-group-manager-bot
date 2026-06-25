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

    # این بخش باعث می‌شود در PV هم کار کند
    if update.message:
        await update.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data.split("_")[0]
    lock_type = query.data.split("_")[1]

    if lock_type not in locks:
        await query.edit_message_text("❌ خطا: قفل نامعتبر است.")
        return

    if action == "lock":
        locks[lock_type] = True
        await query.edit_message_text(f"🔒 قفل {lock_type} فعال شد")
    else:
        locks[lock_type] = False
        await query.edit_message_text(f"🔓 قفل {lock_type} غیرفعال شد")

def get_panel_handlers():
    return [
        CommandHandler("panel", panel),
        CallbackQueryHandler(button_handler),
    ]
