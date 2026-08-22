from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop
from bot.utils.keyboards import (
    get_main_menu, get_admin_menu, get_locks_menu, get_user_menu,
    get_economy_menu, get_entertainment_menu, get_utility_menu, get_settings_menu,
    get_group_settings_menu, get_member_mgmt_menu, get_welcome_settings_menu, get_rules_settings_menu
)
from bot.utils.helpers import is_admin, get_group, get_reply_text
from bot.database.session import get_session


def _inline_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 سرگرمی", callback_data="menu:ent"), InlineKeyboardButton("🛠 کاربردی", callback_data="menu:util")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="menu:account"), InlineKeyboardButton("🏦 بانک و اقتصاد", callback_data="menu:economy")],
        [InlineKeyboardButton("🛡 مدیریت", callback_data="menu:admin"), InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu:settings")],
        [InlineKeyboardButton("🤖 دستیار هوشمند", callback_data="menu:ai"), InlineKeyboardButton("🤝 پشتیبانی", url="https://t.me/sector_ad")],
    ])


def _inline_ent():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😂 جوک", callback_data="act:joke"), InlineKeyboardButton("💡 دانستنی", callback_data="act:fact")],
        [InlineKeyboardButton("❓ معما", callback_data="act:riddle"), InlineKeyboardButton("📖 داستان", callback_data="act:story")],
        [InlineKeyboardButton("📜 فال حافظ", callback_data="act:hafez"), InlineKeyboardButton("🎲 تاس", callback_data="act:dice")],
        [InlineKeyboardButton("🪙 پرتاب سکه", callback_data="act:coin")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _inline_util():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 مترجم", callback_data="util:translate"), InlineKeyboardButton("🧮 ماشین حساب", callback_data="util:calc")],
        [InlineKeyboardButton("⛅️ هواشناسی", callback_data="util:weather"), InlineKeyboardButton("📅 تاریخ و زمان", callback_data="util:time")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")],
    ])


def _inline_back():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منوی اصلی", callback_data="menu:main")]])


async def _cleanup_group_button_press(update: Update):
    if update.effective_chat and update.effective_chat.type != "private" and update.effective_message:
        try:
            await update.effective_message.delete()
        except Exception as e:
            print(f"[TRACE] panel:cleanup_skip | {e}")


async def group_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q:
        return
    await q.answer()
    data = q.data or ""
    chat = update.effective_chat

    if data == "menu:main":
        await q.edit_message_text("🏠 منوی اصلی SectorBot", reply_markup=_inline_main())
        return
    if data == "menu:ent":
        await q.edit_message_text("🎮 سرگرمی و بازی", reply_markup=_inline_ent())
        return
    if data == "menu:util":
        await q.edit_message_text("🛠 ابزارهای کاربردی", reply_markup=_inline_util())
        return
    if data == "menu:ai":
        await q.edit_message_text("🤖 برای گفتگو در گروه، پیام را با «سکتور» شروع کن، منشنم کن یا روی پیام خودم ریپلای کن.", reply_markup=_inline_back())
        return
    if data == "menu:account":
        await q.edit_message_text("👤 حساب کاربری\nبرای جزئیات حساب و پروفایل، این بخش فعلاً از منوی خصوصی کامل‌تر است.", reply_markup=_inline_back())
        return
    if data == "menu:economy":
        await q.edit_message_text("🏦 بانک و اقتصاد\nعملیات مالی حساس فعلاً از چت خصوصی انجام می‌شود تا گروه شلوغ نشود.", reply_markup=_inline_back())
        return
    if data in ("menu:admin", "menu:settings"):
        if not await is_admin(update, context):
            await q.answer("این بخش مخصوص مدیران گروه است.", show_alert=True)
            return
        await q.edit_message_text("🛡 مدیریت گروه\nبرای تنظیمات کامل مدیریتی از /panel استفاده کن؛ این منوی Inline در حال تکمیل است.", reply_markup=_inline_back())
        return

    # Entertainment callbacks work directly, without posting button text into the group.
    if data.startswith("act:"):
        from bot.modules.ai import get_new_joke, get_new_fact, hafez_fortune
        from bot.modules.entertainment import get_riddle_cmd, get_story_cmd, dice_cmd, coin_cmd
        action = data.split(":", 1)[1]
        try:
            if action == "joke":
                await get_new_joke(update, context)
            elif action == "fact":
                await get_new_fact(update, context)
            elif action == "riddle":
                await get_riddle_cmd(update, context)
            elif action == "story":
                await get_story_cmd(update, context)
            elif action == "hafez":
                await hafez_fortune(update, context)
            elif action == "dice":
                await dice_cmd(update, context)
            elif action == "coin":
                await coin_cmd(update, context)
        except ApplicationHandlerStop:
            pass
        return

    if data == "util:translate":
        await q.edit_message_text("🌐 برای ترجمه بنویس:\nترجمه: متن موردنظر", reply_markup=_inline_util())
    elif data == "util:calc":
        await q.edit_message_text("🧮 عبارت را مستقیم بفرست؛ مثال: 10 + 5", reply_markup=_inline_util())
    elif data == "util:weather":
        await q.edit_message_text("⛅️ بنویس: هوای تهران", reply_markup=_inline_util())
    elif data == "util:time":
        import datetime
        now = datetime.datetime.now()
        await q.edit_message_text(f"📅 {now.strftime('%Y-%m-%d')}\n🕒 {now.strftime('%H:%M:%S')}", reply_markup=_inline_util())


async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return
    text = update.effective_message.text
    print(f"[TRACE] panel:menu_navigation_handler | text: {text}")
    handled = True
    await _cleanup_group_button_press(update)

    # Group navigation is now rendered as InlineKeyboard so presses do not become chat messages.
    if update.effective_chat.type != "private" and text in ("🎮 سرگرمی", "🛠 کاربردی", "🔙 بازگشت به منوی اصلی", "🔙 بازگشت به سرگرمی"):
        if text in ("🎮 سرگرمی", "🔙 بازگشت به سرگرمی"):
            await context.bot.send_message(update.effective_chat.id, "🎮 سرگرمی و بازی", reply_markup=_inline_ent())
        elif text == "🛠 کاربردی":
            await context.bot.send_message(update.effective_chat.id, "🛠 ابزارهای کاربردی", reply_markup=_inline_util())
        else:
            await context.bot.send_message(update.effective_chat.id, "🏠 منوی اصلی SectorBot", reply_markup=_inline_main())
    elif text == "🛡 مدیریت":
        if await is_admin(update, context):
            reply = await get_reply_text(update.effective_user, "🛡 منوی مدیریت SectorBot\nیکی از بخش‌ها را انتخاب کنید:")
            await context.bot.send_message(update.effective_chat.id, reply, reply_markup=get_admin_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ این بخش مخصوص مدیران گروه است.")
    elif text == "👤 حساب کاربری":
        await context.bot.send_message(update.effective_chat.id, "👤 تنظیمات و اطلاعات حساب شما:", reply_markup=get_user_menu())
    elif text == "🏦 بانک و اقتصاد":
        await context.bot.send_message(update.effective_chat.id, "🏦 سیستم مالی و پاداش سکتور:", reply_markup=get_economy_menu())
    elif text == "⚙️ تنظیمات":
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات ربات در این گروه:", reply_markup=get_settings_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ فقط مدیران می‌توانند تنظیمات را تغییر دهند.")
    elif text == "🤖 دستیار هوشمند":
        await context.bot.send_message(update.effective_chat.id, "🤖 در گروه من را با «سکتور» صدا بزن، منشن کن یا روی پیامم ریپلای کن.", reply_markup=_inline_main() if update.effective_chat.type != "private" else get_main_menu())
    elif text == "🤝 پشتیبانی":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("👤 ارتباط با کارشناس", url="https://t.me/sector_ad")]])
        await context.bot.send_message(update.effective_chat.id, "🤝 پشتیبانی SectorBot\n\n🆔 @sector_ad", reply_markup=keyboard)
    elif text in ("🔒 قفل‌های گروه", "🔒 قفل‌ها"):
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "🔐 مدیریت قفل‌های محتوا:", reply_markup=get_locks_menu())
    elif text == "👤 مدیریت اعضا":
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "👤 بخش مدیریت اعضا:", reply_markup=get_member_mgmt_menu())
    elif text == "⚙️ تنظیمات گروه":
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات پیشرفته گروه:", reply_markup=get_group_settings_menu())
    elif text == "📊 آمار گروه":
        from bot.modules.profile import group_stats_cmd
        await group_stats_cmd(update, context)
    elif text == "👋 خوشامدگویی":
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "👋 تنظیمات خوشامدگویی:", reply_markup=get_welcome_settings_menu())
    elif text == "📜 قوانین":
        if update.effective_chat.type == "private":
            await context.bot.send_message(update.effective_chat.id, "❌ فقط در گروه‌ها.")
        elif await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "📜 تنظیمات قوانین:", reply_markup=get_rules_settings_menu())
        else:
            from bot.modules.rules import rules_cmd
            await rules_cmd(update, context)
    elif text == "🔙 بازگشت به مدیریت":
        await context.bot.send_message(update.effective_chat.id, "🛡 منوی مدیریت", reply_markup=get_admin_menu())
    else:
        handled = False

    if handled:
        print(f"[TRACE] panel:menu_navigation_handler | handled: {text} | ApplicationHandlerStop")
        raise ApplicationHandlerStop()


async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[TRACE] panel:panel_cmd")
    if update.effective_chat.type == "private":
        reply = await get_reply_text(update.effective_user, "🏠 منوی اصلی SectorBot 2.0\nلطفاً یک بخش را انتخاب کنید:")
        await update.effective_message.reply_text(reply, reply_markup=get_main_menu(), parse_mode=None)
    elif await is_admin(update, context):
        await update.effective_message.reply_text("🏠 منوی اصلی SectorBot", reply_markup=_inline_main())
    else:
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای باز کردن پنل را ندارید.")
    raise ApplicationHandlerStop()


async def toggle_setting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    text = update.effective_message.text
    print(f"[TRACE] panel:toggle_setting_handler | text: {text}")
    await _cleanup_group_button_press(update)
    mapping = {
        "🤖 تنظیمات هوش مصنوعی": "ai_enabled", "💰 تنظیمات اقتصاد": "economy_enabled",
        "🔘 فعال/غیرفعال سازی خوشامدگویی": "welcome_enabled", "🛡 ضد اسپم": "antispam_enabled",
        "🆕 جلوگیری از ورود ربات": "prevent_bots", "👤 محدودیت عضو جدید": "new_member_limit",
        "⏳ تایید عضو جدید": "approval_mode", "📢 گزارش فعالیت": "activity_logging",
        "🔘 فعال/غیرفعال سازی قوانین": "rules_enabled"
    }
    if text in mapping:
        attr = mapping[text]
        session = get_session(); group = get_group(session, update.effective_chat.id)
        if group and hasattr(group, attr):
            setattr(group, attr, not getattr(group, attr)); session.commit()
            status = "فعال" if getattr(group, attr) else "غیرفعال"
            await context.bot.send_message(update.effective_chat.id, f"✅ {text}: {status}")
        session.close()
        raise ApplicationHandlerStop()


def get_panel_handlers():
    nav_regex = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|⚙️ تنظیمات|⚙️ تنظیمات گروه|⚙️ تنظیمات عمومی|👤 مدیریت اعضا|🤖 دستیار هوشمند|🤝 پشتیبانی|🔒 قفل‌های گروه|🔒 قفل‌ها|👋 خوشامدگویی|📜 قوانین|📊 آمار گروه|🔙 بازگشت.*)$"
    toggle_regex = "^(🤖 تنظیمات هوش مصنوعی|💰 تنظیمات اقتصاد|🛡 ضد اسپم|🆕 جلوگیری از ورود ربات|👤 محدودیت عضو جدید|⏳ تایید عضو جدید|📢 گزارش فعالیت|🔘 فعال/غیرفعال سازی خوشامدگویی|🔘 فعال/غیرفعال سازی قوانین)$"
    return [
        CommandHandler("panel", panel_cmd),
        CallbackQueryHandler(group_menu_callback, pattern=r"^(menu|act|util):"),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler),
        MessageHandler(filters.TEXT & filters.Regex(toggle_regex), toggle_setting_handler),
    ]
