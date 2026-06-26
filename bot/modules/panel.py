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

async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    handled = True

    if text == "🛡 مدیریت":
        if await is_admin(update, context):
            reply = await get_reply_text(update.effective_user, "🛡 **منوی مدیریت SectorBot**\nیکی از بخش‌ها را انتخاب کنید:")
            await update.effective_message.reply_text(reply, reply_markup=get_admin_menu(), parse_mode=None)
        else:
            await update.effective_message.reply_text("❌ این بخش مخصوص مدیران گروه است.")

    elif text == "👤 حساب کاربری":
        await update.effective_message.reply_text("👤 **تنظیمات و اطلاعات حساب شما:**", reply_markup=get_user_menu(), parse_mode=None)

    elif text == "🏦 بانک و اقتصاد":
        await update.effective_message.reply_text("🏦 **سیستم مالی و پاداش سکتور:**", reply_markup=get_economy_menu(), parse_mode=None)

    elif text == "🎮 سرگرمی":
        await update.effective_message.reply_text("🎮 **بخش سرگرمی و بازی:**", reply_markup=get_entertainment_menu(), parse_mode=None)

    elif text == "🛠 کاربردی":
        await update.effective_message.reply_text("🛠 **ابزارهای هوشمند و کاربردی:**", reply_markup=get_utility_menu(), parse_mode=None)

    elif text == "⚙️ تنظیمات":
        if await is_admin(update, context):
            await update.effective_message.reply_text("⚙️ **تنظیمات ربات در این گروه:**", reply_markup=get_settings_menu(), parse_mode=None)
        else:
            await update.effective_message.reply_text("❌ فقط مدیران می‌توانند تنظیمات را تغییر دهند.")

    elif text == "🤖 دستیار هوشمند":
        await update.effective_message.reply_text(
            "🤖 **من دستیار هوشمند سکتور هستم!**\n\n"
            "✨ من می‌تونم به سوالاتت جواب بدم، تو پیدا کردن اطلاعات کمکت کنم و باهات گپ بزنم.\n\n"
            "💡 **روش استفاده:**\n"
            "▫️ در چت خصوصی: مستقیماً پیام بده.\n"
            "▫️ در گروه‌ها: اول پیام کلمه **سکتور** یا **Sector** رو بنویس یا منو ریپلای کن.",
            reply_markup=get_main_menu(),
            parse_mode=None
        )

    elif text == "🤝 پشتیبانی":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("👤 ارتباط با کارشناس", url="t.me/sector_ad")]])
        await update.effective_message.reply_text(
            "🤝 **پشتیبانی SectorBot**\n\n"
            "برای ارتباط با پشتیبانی، گزارش مشکل یا سوال:\n\n"
            "🆔 @sector_ad",
            reply_markup=keyboard,
            parse_mode=None
        )

    elif text == "🔒 قفل‌های گروه":
        if await is_admin(update, context):
            await update.effective_message.reply_text("🔐 **مدیریت قفل‌های محتوا:**\nبرای فعال/غیرفعال کردن هر قفل روی دکمه مربوطه بزنید.", reply_markup=get_locks_menu(), parse_mode=None)

    elif text == "👤 مدیریت اعضا":
        if await is_admin(update, context):
            await update.effective_message.reply_text("👤 **بخش مدیریت اعضا:**", reply_markup=get_member_mgmt_menu(), parse_mode=None)

    elif text == "⚙️ تنظیمات گروه":
        if await is_admin(update, context):
            await update.effective_message.reply_text("⚙️ **تنظیمات پیشرفته گروه:**", reply_markup=get_group_settings_menu(), parse_mode=None)

    elif text == "📊 آمار گروه":
         from bot.modules.profile import group_stats_cmd
         await group_stats_cmd(update, context)

    elif text == "👋 خوشامدگویی":
        if await is_admin(update, context):
            await update.effective_message.reply_text("👋 **تنظیمات خوشامدگویی:**", reply_markup=get_welcome_settings_menu())
        else:
            await update.effective_message.reply_text("❌ مخصوص مدیران.")

    elif text == "📜 قوانین":
        if update.effective_chat.type == "private":
            await update.effective_message.reply_text("❌ فقط در گروه‌ها.")
        elif await is_admin(update, context):
            await update.effective_message.reply_text("📜 **تنظیمات قوانین:**", reply_markup=get_rules_settings_menu())
        else:
            from bot.modules.rules import rules_cmd
            await rules_cmd(update, context)

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
        reply = await get_reply_text(update.effective_user, "🏠 **منوی اصلی SectorBot 2.0**\nلطفاً یک بخش را انتخاب کنید:")
        await update.effective_message.reply_text(reply, reply_markup=get_main_menu(), parse_mode=None)
    else:
        await update.effective_message.reply_text("❌ شما دسترسی لازم برای باز کردن پنل را ندارید.")
    raise ApplicationHandlerStop()

async def toggle_setting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    text = update.effective_message.text

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
        if hasattr(group, attr):
            setattr(group, attr, not getattr(group, attr))
            session.commit()
            status = "فعال" if getattr(group, attr) else "غیرفعال"
            await update.effective_message.reply_text(f"✅ تنظیمات **{text}** به حالت **{status}** تغییر یافت.", parse_mode=None)
        session.close()
        raise ApplicationHandlerStop()

def get_panel_handlers():
    nav_regex = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🎮 بازی‌ها|🛠 کاربردی|⚙️ تنظیمات|⚙️ تنظیمات گروه|👤 مدیریت اعضا|🤖 دستیار هوشمند|🤝 پشتیبانی|🔒 قفل‌های گروه|👋 خوشامدگویی|📜 قوانین|📊 آمار گروه|🔙 بازگشت.*)$"
    toggle_regex = "^(🤖 تنظیمات هوش مصنوعی|💰 تنظیمات اقتصاد|🛡 ضد اسپم|🆕 جلوگیری از ورود ربات|👤 محدودیت عضو جدید|⏳ تایید عضو جدید|📢 گزارش فعالیت|🔘 فعال/غیرفعال سازی خوشامدگویی|🔘 فعال/غیرفعال سازی قوانین)$"
    return [
        CommandHandler("panel", panel_cmd),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler),
        MessageHandler(filters.TEXT & filters.Regex(toggle_regex), toggle_setting_handler),
    ]
