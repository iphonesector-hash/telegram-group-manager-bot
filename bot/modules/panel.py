from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.utils.keyboards import (
    get_main_menu, get_admin_menu, get_locks_menu, get_user_menu,
    get_economy_menu, get_entertainment_menu, get_utility_menu, get_settings_menu, get_games_menu,
    get_group_settings_menu, get_member_mgmt_menu
)
from bot.utils.helpers import is_admin, get_group
from bot.database.session import get_session
from bot.database.models import User, Group

async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    handled = True

    if text == "🛡 مدیریت":
        if await is_admin(update, context):
            await update.effective_message.reply_text("🛡 منوی مدیریت SectorBot\nیکی از بخش‌ها را انتخاب کنید:", reply_markup=get_admin_menu(), parse_mode=None)
        else:
            await update.effective_message.reply_text("❌ این بخش مخصوص مدیران گروه است.")

    elif text == "👤 حساب کاربری":
        await update.effective_message.reply_text("👤 تنظیمات و اطلاعات حساب شما:", reply_markup=get_user_menu(), parse_mode=None)

    elif text == "🏦 بانک و اقتصاد":
        await update.effective_message.reply_text("🏦 سیستم مالی و پاداش سکتور:", reply_markup=get_economy_menu(), parse_mode=None)

    elif text == "🎮 سرگرمی":
        await update.effective_message.reply_text("🎮 بخش سرگرمی و بازی:", reply_markup=get_entertainment_menu(), parse_mode=None)

    elif text == "🛠 کاربردی":
        await update.effective_message.reply_text("🛠 ابزارهای هوشمند و کاربردی:", reply_markup=get_utility_menu(), parse_mode=None)

    elif text == "⚙️ تنظیمات":
        if await is_admin(update, context):
            await update.effective_message.reply_text("⚙️ تنظیمات ربات در این گروه:", reply_markup=get_settings_menu(), parse_mode=None)
        else:
            await update.effective_message.reply_text("❌ فقط مدیران می‌توانند تنظیمات را تغییر دهند.")

    elif text == "🤖 دستیار هوشمند":
        await update.effective_message.reply_text(
            "🤖 دستیار هوشمند سکتور هستم!\n\n"
            "✨ من می‌تونم به سوالاتت جواب بدم، تو پیدا کردن اطلاعات کمکت کنم و باهات گپ بزنم.\n\n"
            "💡 روش استفاده:\n"
            "▫️ در چت خصوصی: مستقیماً پیام بده.\n"
            "▫️ در گروه‌ها: اول پیام کلمه سکتور یا Sector رو بنویس یا منو ریپلای کن.",
            reply_markup=get_main_menu(),
            parse_mode=None
        )

    elif text == "🆘 پشتیبانی":
        await update.effective_message.reply_text("🆘 پشتیبانی سکتور\n\nدر صورت بروز مشکل یا داشتن سوال، با تیم پشتیبانی در ارتباط باشید:\n👤 @sector_ad", parse_mode=None)

    elif text == "🔒 قفل‌های گروه":
        if await is_admin(update, context):
            await update.effective_message.reply_text("🔐 مدیریت قفل‌های محتوا:\nبرای فعال/غیرفعال کردن هر قفل روی دکمه مربوطه بزنید.", reply_markup=get_locks_menu(), parse_mode=None)

    elif text == "👤 مدیریت اعضا":
        if await is_admin(update, context):
            await update.effective_message.reply_text("👤 بخش مدیریت اعضا:", reply_markup=get_member_mgmt_menu(), parse_mode=None)

    elif text == "⚙️ تنظیمات گروه":
        if await is_admin(update, context):
            await update.effective_message.reply_text("⚙️ تنظیمات پیشرفته گروه:", reply_markup=get_group_settings_menu(), parse_mode=None)

    elif text == "🎮 بازی‌ها":
        await update.effective_message.reply_text("🎮 لیست بازی‌های موجود:", reply_markup=get_games_menu(), parse_mode=None)

    elif text == "🔙 بازگشت به مدیریت":
        await update.effective_message.reply_text("🛡 بازگشت به منوی مدیریت:", reply_markup=get_admin_menu())

    elif text == "🔙 بازگشت به سرگرمی":
        await update.effective_message.reply_text("🎮 بازگشت به منوی سرگرمی:", reply_markup=get_entertainment_menu())

    elif text == "🔙 بازگشت به منوی اصلی":
        await update.effective_message.reply_text("🏠 بازگشت به منوی اصلی:", reply_markup=get_main_menu())
    else:
        handled = False

    if handled:
        raise ApplicationHandlerStop()

async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private" or await is_admin(update, context):
        await update.effective_message.reply_text("🏠 منوی اصلی SectorBot\nلطفاً یک بخش را انتخاب کنید:", reply_markup=get_main_menu(), parse_mode=None)
    else:
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای باز کردن پنل را ندارید.")

async def toggle_setting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    text = update.effective_message.text

    mapping = {
        "🤖 تنظیمات هوش مصنوعی": "ai_enabled",
        "💰 تنظیمات اقتصاد": "economy_enabled",
        "👋 خوش‌آمدگویی": "welcome_enabled",
        "🛡 ضد اسپم": "antispam_enabled",
        "🆕 جلوگیری از ورود ربات": "prevent_bots",
        "👤 محدودیت عضو جدید": "new_member_limit",
        "⏳ تایید عضو جدید": "approval_mode",
        "📢 گزارش فعالیت": "activity_logging"
    }

    if text in mapping:
        attr = mapping[text]
        session = get_session()
        group = get_group(session, update.effective_chat.id, update.effective_chat.title)
        setattr(group, attr, not getattr(group, attr))
        session.commit()
        status = "فعال" if getattr(group, attr) else "غیرفعال"
        await update.effective_message.reply_text(f"✅ تنظیمات {text} به حالت {status} تغییر یافت.", parse_mode=None)
        session.close()
        raise ApplicationHandlerStop()

def get_panel_handlers():
    nav_regex = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🎮 بازی‌ها|🛠 کاربردی|⚙️ تنظیمات|⚙️ تنظیمات گروه|👤 مدیریت اعضا|🤖 دستیار هوشمند|🆘 پشتیبانی|🔒 قفل‌های گروه|🔙 بازگشت.*)$"
    toggle_regex = "^(🤖 تنظیمات هوش مصنوعی|💰 تنظیمات اقتصاد|👋 خوش‌آمدگویی|🛡 ضد اسپم|🆕 جلوگیری از ورود ربات|👤 محدودیت عضو جدید|⏳ تایید عضو جدید|📢 گزارش فعالیت)$"
    return [
        CommandHandler("panel", panel_cmd),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler),
        MessageHandler(filters.TEXT & filters.Regex(toggle_regex), toggle_setting_handler),
    ]
