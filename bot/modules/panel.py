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

    # این خط باعث می‌شود /panel در PV هم کار کند
    await update.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)
