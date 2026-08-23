from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
import os
from telegram.error import BadRequest, Forbidden
from telegram.ext import ApplicationHandlerStop, CommandHandler, ContextTypes, MessageHandler, filters

from bot.modules.sector_social import show_sector_reply_actions
from bot.utils.helpers import is_admin
from bot.utils.keyboards import (
    get_admin_menu, get_economy_menu, get_entertainment_menu, get_group_settings_menu,
    get_locks_menu, get_main_menu, get_member_mgmt_menu, get_rules_settings_menu,
    get_settings_menu, get_user_menu, get_utility_menu, get_welcome_settings_menu,
)

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0]


async def _delete_group_press(update: Update):
    if update.effective_chat and update.effective_chat.type != "private" and update.effective_message:
        try:
            await update.effective_message.delete()
        except Exception:
            pass


async def _private_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, text, reply_markup):
    """Send personal navigation to DM only; never create a replacement group message."""
    try:
        await context.bot.send_message(update.effective_user.id, text, reply_markup=reply_markup)
        return True
    except (Forbidden, BadRequest):
        return False
    except Exception:
        return False


async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.effective_message.reply_text("🏠 منوی اصلی SectorBot", reply_markup=get_main_menu())
    else:
        await _private_panel(update, context, "🏠 منوی اصلی SectorBot", get_main_menu())
        await _delete_group_press(update)
    raise ApplicationHandlerStop()


async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return
    text = update.effective_message.text.strip()
    private = update.effective_chat.type == "private"

    if not private:
        replied = update.effective_message.reply_to_message
        if text in ("🤖 سکتور کوچولو", "سکتور کوچولو") and replied and replied.from_user and not replied.from_user.is_bot:
            opened = await show_sector_reply_actions(update, context, replied.from_user)
            await _delete_group_press(update)
            if opened:
                raise ApplicationHandlerStop()

        personal = {
            "🎮 سرگرمی": ("🎮 سرگرمی و بازی", get_entertainment_menu()),
            "🛠 کاربردی": ("🛠 ابزارهای کاربردی", get_utility_menu()),
            "👤 حساب کاربری": ("👤 حساب کاربری", get_user_menu()),
            "🏦 بانک و اقتصاد": ("🏦 بانک و اقتصاد", get_economy_menu()),
            "⚙️ تنظیمات": ("⚙️ تنظیمات شخصی", get_settings_menu()),
            "🤖 دستیار هوشمند": ("🤖 همین‌جا هر سوالی داری بپرس.", get_main_menu()),
            "🤖 سکتور کوچولو": ("🤖 سکتور کوچولو", InlineKeyboardMarkup([[
                InlineKeyboardButton("مراقبت در چت", callback_data="sector_pet", style="primary"),
                InlineKeyboardButton("sector", web_app=WebAppInfo(url=MINI_APP_URL)),
            ]])),
            "سکتور کوچولو": ("🤖 سکتور کوچولو", InlineKeyboardMarkup([[
                InlineKeyboardButton("مراقبت در چت", callback_data="sector_pet", style="primary"),
                InlineKeyboardButton("sector", web_app=WebAppInfo(url=MINI_APP_URL)),
            ]])),
            "🤝 پشتیبانی": ("🤝 پشتیبانی: @sector_ad", get_main_menu()),
            "🔙 بازگشت به سرگرمی": ("🎮 سرگرمی و بازی", get_entertainment_menu()),
            "🔙 بازگشت به منوی اصلی": ("🏠 منوی اصلی SectorBot", get_main_menu()),
        }
        if text in personal:
            await _private_panel(update, context, *personal[text])
            await _delete_group_press(update)
            raise ApplicationHandlerStop()

        if text == "🛡 مدیریت":
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "🛡 منوی مدیریت", reply_markup=get_admin_menu())
            raise ApplicationHandlerStop()
        if text in ("🔒 قفل‌های گروه", "🔒 قفل‌ها"):
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "🔐 مدیریت قفل‌ها", reply_markup=get_locks_menu())
            raise ApplicationHandlerStop()
        if text == "👤 مدیریت اعضا":
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "👤 مدیریت اعضا", reply_markup=get_member_mgmt_menu())
            raise ApplicationHandlerStop()
        if text == "⚙️ تنظیمات گروه":
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات گروه", reply_markup=get_group_settings_menu())
            raise ApplicationHandlerStop()
        if text == "👋 خوشامدگویی":
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "👋 تنظیمات خوشامدگویی", reply_markup=get_welcome_settings_menu())
            raise ApplicationHandlerStop()
        if text == "📜 قوانین":
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "📜 تنظیمات قوانین", reply_markup=get_rules_settings_menu())
            raise ApplicationHandlerStop()
        if text == "🔙 بازگشت به مدیریت":
            await _delete_group_press(update)
            if await is_admin(update, context):
                await context.bot.send_message(update.effective_chat.id, "🛡 منوی مدیریت", reply_markup=get_admin_menu())
            raise ApplicationHandlerStop()
        return

    if text == "🎮 سرگرمی":
        await update.effective_message.reply_text("🎮 سرگرمی و بازی", reply_markup=get_entertainment_menu())
    elif text == "🛠 کاربردی":
        await update.effective_message.reply_text("🛠 ابزارهای کاربردی", reply_markup=get_utility_menu())
    elif text == "👤 حساب کاربری":
        await update.effective_message.reply_text("👤 حساب کاربری", reply_markup=get_user_menu())
    elif text == "🏦 بانک و اقتصاد":
        await update.effective_message.reply_text("🏦 بانک و اقتصاد", reply_markup=get_economy_menu())
    elif text == "🛡 مدیریت":
        await update.effective_message.reply_text("🛡 مدیریت فقط داخل گروه قابل استفاده است.", reply_markup=get_main_menu())
    elif text == "⚙️ تنظیمات":
        await update.effective_message.reply_text("⚙️ تنظیمات", reply_markup=get_settings_menu())
    elif text == "🤖 دستیار هوشمند":
        await update.effective_message.reply_text("🤖 همین‌جا هر سوالی داری بپرس.", reply_markup=get_main_menu())
    elif text in ("🤖 سکتور کوچولو", "سکتور کوچولو"):
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("مراقبت در چت", callback_data="sector_pet", style="primary"),
            InlineKeyboardButton("sector", web_app=WebAppInfo(url=MINI_APP_URL)),
        ]])
        await update.effective_message.reply_text("🤖 سکتور کوچولو همراه دیجیتال توئه؛ با سکه، مأموریت، بازی و تمرین کمکش کن رشد کنه!", reply_markup=markup)
    elif text == "🤝 پشتیبانی":
        await update.effective_message.reply_text("🤝 پشتیبانی: @sector_ad", reply_markup=get_main_menu())
    elif text == "📜 قوانین":
        await update.effective_message.reply_text("📜 قوانین فقط برای گروه کاربرد دارد.", reply_markup=get_main_menu())
    elif text == "🔙 بازگشت به سرگرمی":
        await update.effective_message.reply_text("🎮 سرگرمی و بازی", reply_markup=get_entertainment_menu())
    elif text == "🔙 بازگشت به منوی اصلی":
        await update.effective_message.reply_text("🏠 منوی اصلی SectorBot", reply_markup=get_main_menu())
    else:
        return
    raise ApplicationHandlerStop()


def get_panel_handlers():
    nav_regex = (
        "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|⚙️ تنظیمات|🤖 دستیار هوشمند|🤖 سکتور کوچولو|سکتور کوچولو|🤝 پشتیبانی|"
        "🔒 قفل‌های گروه|🔒 قفل‌ها|👤 مدیریت اعضا|⚙️ تنظیمات گروه|👋 خوشامدگویی|📜 قوانین|"
        "🔙 بازگشت به مدیریت|🔙 بازگشت به منوی اصلی|🔙 بازگشت به سرگرمی)$"
    )
    return [CommandHandler("panel", panel_cmd), MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler)]
