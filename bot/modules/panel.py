from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.utils.keyboards import (
    get_main_menu, get_admin_menu, get_locks_menu, get_user_menu,
    get_economy_menu, get_entertainment_menu, get_utility_menu, get_settings_menu, get_games_menu,
    get_group_settings_menu, get_member_mgmt_menu, get_welcome_settings_menu, get_rules_settings_menu
)
from bot.utils.helpers import is_admin, get_group, get_reply_text
from bot.database.session import get_session
from bot.database.models import User, Group

async def _cleanup_group_button_press(update: Update):
    if update.effective_chat and update.effective_chat.type != "private" and update.effective_message:
        try:
            await update.effective_message.delete()
        except Exception as e:
            print(f"[TRACE] panel:cleanup_skip | {e}")

async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    print(f"[TRACE] panel:menu_navigation_handler | text: {text}")
    handled = True

    # In groups, ReplyKeyboard presses are ordinary chat messages. Remove the trigger
    # after we receive it so the management UI does not pollute the conversation.
    await _cleanup_group_button_press(update)

    if text == "🛡 مدیریت":
        if await is_admin(update, context):
            reply = await get_reply_text(update.effective_user, "🛡 منوی مدیریت SectorBot\nیکی از بخش‌ها را انتخاب کنید:")
            await context.bot.send_message(update.effective_chat.id, reply, reply_markup=get_admin_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ این بخش مخصوص مدیران گروه است.")

    elif text == "👤 حساب کاربری":
        await context.bot.send_message(update.effective_chat.id, "👤 تنظیمات و اطلاعات حساب شما:", reply_markup=get_user_menu())

    elif text == "🏦 بانک و اقتصاد":
        await context.bot.send_message(update.effective_chat.id, "🏦 سیستم مالی و پاداش سکتور:", reply_markup=get_economy_menu())

    elif text == "🎮 سرگرمی":
        await context.bot.send_message(update.effective_chat.id, "🎮 بخش سرگرمی و بازی:", reply_markup=get_entertainment_menu())

    elif text == "🛠 کاربردی":
        await context.bot.send_message(update.effective_chat.id, "🛠 ابزارهای هوشمند و کاربردی:", reply_markup=get_utility_menu())

    elif text == "⚙️ تنظیمات":
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات ربات در این گروه:", reply_markup=get_settings_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ فقط مدیران می‌توانند تنظیمات را تغییر دهند.")

    elif text == "⚙️ تنظیمات عمومی":
        if await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات عمومی گروه:", reply_markup=get_group_settings_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ فقط مدیران.")

    elif text == "🤖 دستیار هوشمند":
        await context.bot.send_message(
            update.effective_chat.id,
            "🤖 من دستیار هوشمند سکتور هستم!\n\n"
            "✨ می‌تونم به سوالاتت جواب بدم و باهات گپ بزنم.\n\n"
            "💡 روش استفاده:\n"
            "▫️ در چت خصوصی: مستقیماً پیام بده.\n"
            "▫️ در گروه: پیام را با «سکتور» یا «Sector» شروع کن، من را منشن کن، یا روی پیام خودم ریپلای کن.",
            reply_markup=get_main_menu()
        )

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
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ مخصوص مدیران.")

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

    elif text == "🔙 بازگشت به سرگرمی":
        await context.bot.send_message(update.effective_chat.id, "🎮 سرگرمی", reply_markup=get_entertainment_menu())

    elif text == "🔙 بازگشت به منوی اصلی":
        await context.bot.send_message(update.effective_chat.id, "🏠 منوی اصلی SectorBot", reply_markup=get_main_menu())
    else:
        handled = False

    if handled:
        print(f"[TRACE] panel:menu_navigation_handler | handled: {text} | ApplicationHandlerStop")
        raise ApplicationHandlerStop()

async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[TRACE] panel:panel_cmd")
    if update.effective_chat.type == "private" or await is_admin(update, context):
        reply = await get_reply_text(update.effective_user, "🏠 منوی اصلی SectorBot 2.0\nلطفاً یک بخش را انتخاب کنید:")
        await update.effective_message.reply_text(reply, reply_markup=get_main_menu(), parse_mode=None)
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
        "🤖 تنظیمات هوش مصنوعی": "ai_enabled",
        "💰 تنظیمات اقتصاد": "economy_enabled",
        "🔘 فعال/غیرفعال سازی خوشامدگویی": "welcome_enabled",
        "🛡 ضد اسپم": "antispam_enabled",
        "🆕 جلوگیری از ورود ربات": "prevent_bots",
        "👤 محدودیت عضو جدید": "new_member_limit",
        "⏳ تایید عضو جدید": "approval_mode",
        "📢 گزارش فعالیت": "activity_logging",
        "🔘 فعال/غیرفعال سازی قوانین": "rules_enabled"
    }

    if text in mapping:
        attr = mapping[text]
        session = get_session()
        group = get_group(session, update.effective_chat.id)
        if group and hasattr(group, attr):
            setattr(group, attr, not getattr(group, attr))
            session.commit()
            status = "فعال" if getattr(group, attr) else "غیرفعال"
            await context.bot.send_message(update.effective_chat.id, f"✅ {text}: {status}")
        session.close()
        print(f"[TRACE] panel:toggle_setting_handler | handled: {text} | ApplicationHandlerStop")
        raise ApplicationHandlerStop()

def get_panel_handlers():
    nav_regex = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|⚙️ تنظیمات|⚙️ تنظیمات گروه|⚙️ تنظیمات عمومی|👤 مدیریت اعضا|🤖 دستیار هوشمند|🤝 پشتیبانی|🔒 قفل‌های گروه|🔒 قفل‌ها|👋 خوشامدگویی|📜 قوانین|📊 آمار گروه|🔙 بازگشت.*)$"
    toggle_regex = "^(🤖 تنظیمات هوش مصنوعی|💰 تنظیمات اقتصاد|🛡 ضد اسپم|🆕 جلوگیری از ورود ربات|👤 محدودیت عضو جدید|⏳ تایید عضو جدید|📢 گزارش فعالیت|🔘 فعال/غیرفعال سازی خوشامدگویی|🔘 فعال/غیرفعال سازی قوانین)$"
    return [
        CommandHandler("panel", panel_cmd),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler),
        MessageHandler(filters.TEXT & filters.Regex(toggle_regex), toggle_setting_handler),
    ]
