from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.utils.keyboards import (
    get_main_menu, get_admin_menu, get_locks_menu, get_user_menu,
    get_economy_menu, get_entertainment_menu, get_utility_menu, get_settings_menu, get_games_menu
)
from bot.utils.helpers import is_admin
from bot.database.session import get_session
from bot.database.models import User, Group

async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    handled = True

    if text == "🛡 مدیریت":
        if await is_admin(update, context):
            await update.message.reply_text("🛡 **منوی مدیریت SectorBot**\nیکی از بخش‌ها را انتخاب کنید:", reply_markup=get_admin_menu(), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ این بخش مخصوص مدیران گروه است.")

    elif text == "👤 حساب کاربری":
        await update.message.reply_text("👤 **تنظیمات و اطلاعات حساب شما:**", reply_markup=get_user_menu(), parse_mode="Markdown")

    elif text == "🏦 بانک و اقتصاد":
        await update.message.reply_text("🏦 **سیستم مالی و پاداش سکتور:**", reply_markup=get_economy_menu(), parse_mode="Markdown")

    elif text == "🎮 سرگرمی":
        await update.message.reply_text("🎮 **بخش سرگرمی و بازی:**", reply_markup=get_entertainment_menu(), parse_mode="Markdown")

    elif text == "🛠 کاربردی":
        await update.message.reply_text("🛠 **ابزارهای هوشمند و کاربردی:**", reply_markup=get_utility_menu(), parse_mode="Markdown")

    elif text == "⚙️ تنظیمات":
        if await is_admin(update, context):
            await update.message.reply_text("⚙️ **تنظیمات ربات در این گروه:**", reply_markup=get_settings_menu(), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ فقط مدیران می‌توانند تنظیمات را تغییر دهند.")

    elif text == "🤖 دستیار هوشمند":
        await update.message.reply_text(
            "🤖 **من دستیار هوشمند سکتور هستم!**\n\n"
            "✨ من می‌تونم به سوالاتت جواب بدم، تو پیدا کردن اطلاعات کمکت کنم و باهات گپ بزنم.\n\n"
            "💡 **روش استفاده:**\n"
            "▫️ در چت خصوصی: مستقیماً پیام بده.\n"
            "▫️ در گروه‌ها: اول پیام کلمه **سکتور** یا **Sector** رو بنویس یا منو ریپلای کن.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

    elif text == "🆘 پشتیبانی":
        await update.message.reply_text("🆘 **پشتیبانی سکتور**\n\nدر صورت بروز مشکل یا داشتن سوال، با تیم پشتیبانی در ارتباط باشید:\n👤 @sector_ad", parse_mode="Markdown")

    elif text == "🔒 قفل‌های گروه":
        if await is_admin(update, context):
            await update.message.reply_text("🔐 **مدیریت قفل‌های محتوا:**\nبرای فعال/غیرفعال کردن هر قفل روی دکمه مربوطه بزنید.", reply_markup=get_locks_menu(), parse_mode="Markdown")

    elif text == "🎮 بازی‌ها":
        await update.message.reply_text("🎮 **لیست بازی‌های موجود:**", reply_markup=get_games_menu(), parse_mode="Markdown")

    elif text == "🔙 بازگشت به مدیریت":
        await update.message.reply_text("🛡 بازگشت به منوی مدیریت:", reply_markup=get_admin_menu())

    elif text == "🔙 بازگشت به سرگرمی":
        await update.message.reply_text("🎮 بازگشت به منوی سرگرمی:", reply_markup=get_entertainment_menu())

    elif text == "🔙 بازگشت به منوی اصلی":
        await update.message.reply_text("🏠 بازگشت به منوی اصلی:", reply_markup=get_main_menu())
    else:
        handled = False

    if handled:
        raise ApplicationHandlerStop()

async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private" or await is_admin(update, context):
        await update.message.reply_text("🏠 **منوی اصلی SectorBot**\nلطفاً یک بخش را انتخاب کنید:", reply_markup=get_main_menu(), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ شما دسترسی لازم برای باز کردن پنل را ندارید.")

async def ai_toggle_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)
    group.ai_enabled = not group.ai_enabled
    session.commit()
    status = "فعال" if group.ai_enabled else "غیرفعال"
    await update.message.reply_text(f"🤖 دسترسی به هوش مصنوعی در این گروه **{status}** شد.", parse_mode="Markdown")
    session.close()
    raise ApplicationHandlerStop()

async def eco_toggle_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    session = get_session()
    group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
    if not group:
        group = Group(id=update.effective_chat.id, title=update.effective_chat.title)
        session.add(group)
    group.economy_enabled = not group.economy_enabled
    session.commit()
    status = "فعال" if group.economy_enabled else "غیرفعال"
    await update.message.reply_text(f"💰 سیستم اقتصاد در این گروه **{status}** شد.", parse_mode="Markdown")
    session.close()
    raise ApplicationHandlerStop()

def get_panel_handlers():
    nav_regex = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🎮 بازی‌ها|🛠 کاربردی|⚙️ تنظیمات|🤖 دستیار هوشمند|🆘 پشتیبانی|🔒 قفل‌های گروه|🔙 بازگشت.*)$"
    return [
        CommandHandler("panel", panel_cmd),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler),
        MessageHandler(filters.TEXT & filters.Regex("^🤖 تنظیمات هوش مصنوعی$"), ai_toggle_button_handler),
        MessageHandler(filters.TEXT & filters.Regex("^💰 تنظیمات اقتصاد$"), eco_toggle_button_handler),
    ]
