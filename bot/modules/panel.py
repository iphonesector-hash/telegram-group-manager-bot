from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
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

    # Main categories
    keyboard = [
        [
            InlineKeyboardButton("🛡 مدیریت", callback_data="cat_admin"),
            InlineKeyboardButton("👤 کاربر", callback_data="cat_user"),
        ],
        [
            InlineKeyboardButton("🏦 بانک", callback_data="cat_bank"),
            InlineKeyboardButton("🎮 سرگرمی", callback_data="cat_fun"),
        ],
        [
            InlineKeyboardButton("🛠 کاربردی", callback_data="cat_tools"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="cat_settings"),
        ],
        [
            InlineKeyboardButton("🆘 پشتیبانی", url="https://t.me/sector_ad"),
        ],
        [
            InlineKeyboardButton("❌ بستن منو", callback_data="panel_close"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "💎 **منوی هوشمند ربات SectorBot**\nخوش آمدید! لطفاً دسته‌بندی مورد نظر را انتخاب کنید:"

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "panel_close":
        await query.message.delete()
        return

    if data == "panel_main":
        await panel(update, context)
        return

    # Categories
    if data == "cat_admin":
        if not await is_admin(update, context):
            await query.answer("❌ این بخش مخصوص ادمین‌ها است.", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("🔒 قفل‌ها", callback_data="panel_locks")],
            [InlineKeyboardButton("👋 خوش‌آمدگویی", callback_data="panel_welcome")],
            [InlineKeyboardButton("⚠️ هشدارها", callback_data="panel_users")],
            [InlineKeyboardButton("⚙️ تنظیمات گروه", callback_data="cat_settings")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🛡 **بخش مدیریت گروه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "cat_user":
        keyboard = [
            [InlineKeyboardButton("👤 پروفایل", callback_data="user_profile")],
            [InlineKeyboardButton("🏆 رتبه‌بندی", callback_data="user_top")],
            [InlineKeyboardButton("📜 قوانین", callback_data="panel_rules")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("👤 **بخش کاربری:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "cat_bank":
        keyboard = [
            [InlineKeyboardButton("💰 کیف پول", callback_data="bank_wallet"), InlineKeyboardButton("🎁 جایزه روزانه", callback_data="bank_daily")],
            [InlineKeyboardButton("📥 واریز", callback_data="bank_soon"), InlineKeyboardButton("📤 برداشت", callback_data="bank_soon")],
            [InlineKeyboardButton("💸 انتقال سکه", callback_data="bank_soon")],
            [InlineKeyboardButton("💎 ثروتمندترین‌ها", callback_data="user_top")],
            [InlineKeyboardButton("🏦 وام", callback_data="bank_soon"), InlineKeyboardButton("💳 پرداخت وام", callback_data="bank_soon")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🏦 **بانک SectorBot:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "cat_fun":
        keyboard = [
            [InlineKeyboardButton("😂 جوک", callback_data="fun_joke"), InlineKeyboardButton("📜 فال حافظ", callback_data="fun_soon")],
            [InlineKeyboardButton("💡 فکت", callback_data="fun_fact"), InlineKeyboardButton("🔥 انگیزشی", callback_data="fun_soon")],
            [InlineKeyboardButton("📝 متن", callback_data="fun_story"), InlineKeyboardButton("🎲 تاس", callback_data="fun_dice")],
            [InlineKeyboardButton("🪙 شیر یا خط", callback_data="fun_coin"), InlineKeyboardButton("❓ چیستان", callback_data="fun_riddle")],
            [InlineKeyboardButton("🎮 سنگ کاغذ قیچی", callback_data="fun_soon")],
            [InlineKeyboardButton("🔡 حدس کلمه", callback_data="fun_soon"), InlineKeyboardButton("🏳️ حدس پرچم", callback_data="fun_soon")],
            [InlineKeyboardButton("⚔️ دوئل", callback_data="fun_soon"), InlineKeyboardButton("👮 دزد و پلیس", callback_data="fun_soon")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🎮 **بخش سرگرمی و بازی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "cat_tools":
        keyboard = [
            [InlineKeyboardButton("🌍 مترجم", callback_data="tool_soon"), InlineKeyboardButton("☁️ آب و هوا", callback_data="tool_soon")],
            [InlineKeyboardButton("⚖️ تبدیل واحد", callback_data="tool_soon"), InlineKeyboardButton("🧮 حسابگر", callback_data="tool_soon")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("🛠 **ابزارهای کاربردی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "cat_settings":
        if not await is_admin(update, context):
            await query.answer("❌ دسترسی محدود به ادمین.", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("👋 خوش‌آمدگویی", callback_data="panel_welcome")],
            [InlineKeyboardButton("🔒 قفل‌ها", callback_data="panel_locks")],
            [InlineKeyboardButton("🛡 ضداسپم", callback_data="panel_antispam")],
            [InlineKeyboardButton("📜 قوانین", callback_data="panel_rules")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="panel_main")]
        ]
        await query.edit_message_text("⚙️ **تنظیمات پیشرفته گروه:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # Sub-menus logic integration
    elif data == "panel_locks":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        if not group:
            await query.answer("❌ گروه در دیتابیس یافت نشد.")
            session.close()
            return
        def s(v): return "🔒" if v else "🔓"
        keyboard = [
            [InlineKeyboardButton(f"{s(group.lock_links)} لینک", callback_data="toggle_lock_links"), InlineKeyboardButton(f"{s(group.lock_usernames)} یوزرنیم", callback_data="toggle_lock_usernames")],
            [InlineKeyboardButton(f"{s(group.lock_forward)} فوروارد", callback_data="toggle_lock_forward"), InlineKeyboardButton(f"{s(group.lock_photos)} عکس", callback_data="toggle_lock_photos")],
            [InlineKeyboardButton(f"{s(group.lock_stickers)} استیکر", callback_data="toggle_lock_stickers"), InlineKeyboardButton(f"{s(group.lock_gifs)} گیف", callback_data="toggle_lock_gifs")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="cat_admin")]
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
            [InlineKeyboardButton("🔙 بازگشت", callback_data="cat_admin")]
        ]
        await query.edit_message_text("🌟 **تنظیمات خوشامدگویی:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        session.close()

    elif data == "panel_antispam":
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        status = "✅ فعال" if group.antispam_enabled else "❌ غیرفعال"
        keyboard = [
            [InlineKeyboardButton(f"وضعیت: {status}", callback_data="toggle_antispam_enabled")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="cat_settings")]
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
        # Refresh logic
        if "lock" in data: query.data = "panel_locks"
        elif "welcome" in data: query.data = "panel_welcome"
        elif "antispam" in data: query.data = "panel_antispam"
        await button_handler(update, context)

    # Specific Feature Handlers (Redirect to existing commands or logic)
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

    elif data == "fun_joke":
        from bot.modules.entertainment import joke_cmd
        await joke_cmd(update, context)

    elif data == "fun_fact":
        from bot.modules.entertainment import fact_cmd
        await fact_cmd(update, context)

    elif data == "fun_story":
        from bot.modules.entertainment import story_cmd
        await story_cmd(update, context)

    elif data == "fun_dice":
        from bot.modules.entertainment import dice_cmd
        await dice_cmd(update, context)

    elif data == "fun_coin":
        from bot.modules.entertainment import coin_cmd
        await coin_cmd(update, context)

    elif data == "fun_riddle":
        from bot.modules.entertainment import riddle_cmd
        await riddle_cmd(update, context)

    # Placeholders
    elif "_soon" in data:
        await query.answer("🚀 این قابلیت به زودی در آپدیت‌های بعدی اضافه خواهد شد!", show_alert=True)

    elif data == "panel_rules":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="cat_user")]]
        await query.edit_message_text("📜 برای تنظیم قوانین از دستور `/setrules متن قوانین` استفاده کنید.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "panel_users":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="cat_admin")]]
        await query.edit_message_text("👤 **مدیریت کاربران**\nبرای مدیریت کاربران از دستورات زیر استفاده کنید:\n\n/warn - اخطار به کاربر\n/mute - بی‌صدا کردن\n/ban - اخراج و مسدود کردن\n/unmute - آزاد کردن کاربر", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "panel_setwelcome":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="panel_welcome")]]
        await query.edit_message_text("📝 **تنظیم متن خوشامد**\nبرای تغییر متن خوشامد از دستور زیر استفاده کنید:\n\n`/setwelcome متن جدید`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def get_panel_handlers():
    return [
        CommandHandler("panel", panel),
        CallbackQueryHandler(button_handler),
    ]
