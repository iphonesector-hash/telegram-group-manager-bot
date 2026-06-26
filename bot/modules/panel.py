from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import Group, User, Warning

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == "private":
        return True
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        return

    # Main categories as ReplyKeyboardMarkup
    keyboard = [
        ["🛡 مدیریت", "👤 کاربر"],
        ["🏦 بانک", "🎮 سرگرمی"],
        ["🛠 کاربردی", "⚙️ تنظیمات"],
        ["🆘 پشتیبانی"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = "💎 **به منوی هوشمند SectorBot خوش آمدید!**\nلطفاً از دکمه‌های زیر برای دسترسی به بخش‌های مختلف استفاده کنید:"

    await update.effective_message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def menu_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛡 مدیریت":
        if not await is_admin(update, context):
            await update.message.reply_text("❌ این بخش مخصوص ادمین‌ها است.")
            return
        keyboard = [
            [InlineKeyboardButton("🔒 قفل‌ها", callback_data="panel_locks")],
            [InlineKeyboardButton("👋 خوش‌آمدگویی", callback_data="panel_welcome")],
            [InlineKeyboardButton("⚠️ هشدارها", callback_data="panel_users")],
            [InlineKeyboardButton("⚙️ تنظیمات گروه", callback_data="cat_settings")],
            [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
        ]
        await update.message.reply_text("🛡 **بخش مدیریت گروه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "👤 کاربر":
        keyboard = [
            [InlineKeyboardButton("👤 پروفایل", callback_data="user_profile")],
            [InlineKeyboardButton("🏆 رتبه‌بندی", callback_data="user_top")],
            [InlineKeyboardButton("📜 قوانین", callback_data="panel_rules")],
            [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
        ]
        await update.message.reply_text("👤 **بخش کاربری:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "🏦 بانک":
        keyboard = [
            [InlineKeyboardButton("💰 کیف پول", callback_data="bank_wallet"), InlineKeyboardButton("🎁 جایزه روزانه", callback_data="bank_daily")],
            [InlineKeyboardButton("💸 انتقال سکه", callback_data="bank_transfer")],
            [InlineKeyboardButton("💎 ثروتمندترین‌ها", callback_data="user_top")],
            [InlineKeyboardButton("🏦 وام", callback_data="bank_loan"), InlineKeyboardButton("💳 پرداخت وام", callback_data="bank_repay")],
            [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
        ]
        await update.message.reply_text("🏦 **بانک SectorBot:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "🎮 سرگرمی":
        keyboard = [
            [InlineKeyboardButton("😂 جوک", callback_data="fun_joke"), InlineKeyboardButton("📜 فال حافظ", callback_data="fun_hafez")],
            [InlineKeyboardButton("💡 فکت", callback_data="fun_fact"), InlineKeyboardButton("🎲 تاس", callback_data="fun_dice")],
            [InlineKeyboardButton("🪙 شیر یا خط", callback_data="fun_coin"), InlineKeyboardButton("❓ چیستان", callback_data="fun_riddle")],
            [InlineKeyboardButton("🎮 سنگ کاغذ قیچی", callback_data="fun_rps")],
            [InlineKeyboardButton("🔡 حدس کلمه", callback_data="fun_guess_word"), InlineKeyboardButton("🏳️ حدس پرچم", callback_data="fun_guess_flag")],
            [InlineKeyboardButton("⚔️ دوئل", callback_data="fun_duel"), InlineKeyboardButton("👮 دزد و پلیس", callback_data="fun_cops")],
            [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
        ]
        await update.message.reply_text("🎮 **بخش سرگرمی و بازی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "🛠 کاربردی":
        keyboard = [
            [InlineKeyboardButton("🌍 مترجم", callback_data="tool_translate"), InlineKeyboardButton("☁️ آب و هوا", callback_data="tool_weather")],
            [InlineKeyboardButton("⚖️ تبدیل واحد", callback_data="tool_convert"), InlineKeyboardButton("🧮 حسابگر", callback_data="tool_calc")],
            [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
        ]
        await update.message.reply_text("🛠 **ابزارهای کاربردی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "⚙️ تنظیمات":
        if not await is_admin(update, context):
            await update.message.reply_text("❌ دسترسی محدود به ادمین.")
            return
        keyboard = [
            [InlineKeyboardButton("👋 خوش‌آمدگویی", callback_data="panel_welcome")],
            [InlineKeyboardButton("🔒 قفل‌ها", callback_data="panel_locks")],
            [InlineKeyboardButton("🛡 ضداسپم", callback_data="panel_antispam")],
            [InlineKeyboardButton("📜 قوانین", callback_data="panel_rules")],
            [InlineKeyboardButton("❌ بستن", callback_data="panel_close")]
        ]
        await update.message.reply_text("⚙️ **تنظیمات پیشرفته گروه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif text == "🆘 پشتیبانی":
        keyboard = [[InlineKeyboardButton("💬 تماس با پشتیبانی", url="https://t.me/sector_ad")]]
        await update.message.reply_text("🆘 برای پشتیبانی و سوالات، روی دکمه زیر کلیک کنید:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "panel_close":
        await query.message.delete()
        return

    # Category Sub-menus logic
    if data == "panel_locks":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        if not group:
            session.close()
            return
        def s(v): return "🔒" if v else "🔓"
        keyboard = [
            [InlineKeyboardButton(f"{s(group.lock_links)} لینک", callback_data="toggle_lock_links"), InlineKeyboardButton(f"{s(group.lock_usernames)} یوزرنیم", callback_data="toggle_lock_usernames")],
            [InlineKeyboardButton(f"{s(group.lock_forward)} فوروارد", callback_data="toggle_lock_forward"), InlineKeyboardButton(f"{s(group.lock_photos)} عکس", callback_data="toggle_lock_photos")],
            [InlineKeyboardButton(f"{s(group.lock_stickers)} استیکر", callback_data="toggle_lock_stickers"), InlineKeyboardButton(f"{s(group.lock_gifs)} گیف", callback_data="toggle_lock_gifs")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_admin")]
        ]
        await query.edit_message_text("🔐 **تنظیمات قفل‌های گروه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data == "panel_welcome":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        status = "✅ فعال" if group.welcome_enabled else "❌ غیرفعال"
        keyboard = [
            [InlineKeyboardButton(f"وضعیت: {status}", callback_data="toggle_welcome_enabled")],
            [InlineKeyboardButton("📝 تغییر متن خوشامد", callback_data="panel_setwelcome")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_admin")]
        ]
        await query.edit_message_text("🌟 **تنظیمات خوشامدگویی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data == "panel_antispam":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        status = "✅ فعال" if group.antispam_enabled else "❌ غیرفعال"
        keyboard = [
            [InlineKeyboardButton(f"وضعیت: {status}", callback_data="toggle_antispam_enabled")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_settings")]
        ]
        await query.edit_message_text("🛡 **تنظیمات ضد اسپم:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data.startswith("toggle_"):
        attr = data.replace("toggle_", "")
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        if hasattr(group, attr):
            setattr(group, attr, not getattr(group, attr))
            session.commit()
        session.close()
        if "lock" in data: query.data = "panel_locks"
        elif "welcome" in data: query.data = "panel_welcome"
        elif "antispam" in data: query.data = "panel_antispam"
        await button_handler(update, context)

    # Modules Integrations
    elif data == "user_profile":
        from bot.modules.profile import profile_cmd
        await profile_cmd(update, context)
    elif data == "user_top":
        from bot.modules.profile import top_cmd
        await top_cmd(update, context)
    elif data == "bank_wallet":
        from bot.modules.economy import coins_cmd
        await coins_cmd(update, context)
    elif data == "bank_daily":
        from bot.modules.economy import daily_cmd
        await daily_cmd(update, context)
    elif data == "bank_transfer":
        await query.message.reply_text("💸 برای انتقال سکه از دستور زیر استفاده کنید:\n`/transfer آیدی_عددی مبلغ`", parse_mode="Markdown")
    elif data == "bank_loan":
        from bot.modules.economy import loan_cmd
        await loan_cmd(update, context)
    elif data == "bank_repay":
        from bot.modules.economy import repay_cmd
        await repay_cmd(update, context)

    elif data == "fun_joke":
        from bot.modules.entertainment import joke_cmd
        await joke_cmd(update, context)
    elif data == "fun_fact":
        from bot.modules.entertainment import fact_cmd
        await fact_cmd(update, context)
    elif data == "fun_dice":
        from bot.modules.entertainment import dice_cmd
        await dice_cmd(update, context)
    elif data == "fun_coin":
        from bot.modules.entertainment import coin_cmd
        await coin_cmd(update, context)
    elif data == "fun_riddle":
        from bot.modules.entertainment import riddle_cmd
        await riddle_cmd(update, context)
    elif data.startswith("fun_") or data.startswith("tool_"):
        await query.message.reply_text("🚀 این قابلیت به زودی در آپدیت بعدی فعال می‌شود!")

    elif data == "panel_rules":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_user")]]
        await query.edit_message_text("📜 برای تنظیم قوانین از دستور `/setrules متن قوانین` استفاده کنید.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "panel_users":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_admin")]]
        await query.edit_message_text("👤 **مدیریت کاربران**\nبرای مدیریت کاربران از دستورات زیر استفاده کنید:\n\n/warn - اخطار\n/mute - بی‌صدا\n/ban - اخراج\n/unmute - آزاد کردن", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("back_"):
        cat = data.replace("back_", "")
        update.message = query.message
        update.message.text = "🛡 مدیریت" if cat == "admin" else "👤 کاربر" if cat == "user" else "⚙️ تنظیمات"
        await menu_text_handler(update, context)

def get_panel_handlers():
    return [
        CommandHandler("panel", panel),
        MessageHandler(filters.Text(["🛡 مدیریت", "👤 کاربر", "🏦 بانک", "🎮 سرگرمی", "🛠 کاربردی", "⚙️ تنظیمات", "🆘 پشتیبانی"]), menu_text_handler),
        CallbackQueryHandler(button_handler),
    ]
