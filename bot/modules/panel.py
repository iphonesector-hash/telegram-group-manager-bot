from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import os
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.utils.keyboards import (
    get_main_menu, get_admin_menu, get_user_menu, get_economy_menu,
    get_entertainment_menu, get_utility_menu, get_settings_menu,
    get_locks_menu, get_group_settings_menu, get_member_mgmt_menu,
    get_welcome_settings_menu, get_rules_settings_menu,
)
from bot.utils.helpers import is_admin
from bot.services.miniapp_launch import create_launch_url

MINI_APP_URL=os.getenv("MINI_APP_URL","https://isectorland-miniapp.vercel.app").split("?",1)[0]+"?v=20260823-3"


async def _delete_group_press(update: Update):
    if update.effective_chat and update.effective_chat.type != "private" and update.effective_message:
        try:
            await update.effective_message.delete()
        except Exception:
            pass


async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sending a new ReplyKeyboardMarkup replaces any keyboard left by another bot.
    await update.effective_message.reply_text(
        "🏠 منوی اصلی SectorBot",
        reply_markup=get_main_menu(),
    )
    raise ApplicationHandlerStop()


async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text.strip()
    private = update.effective_chat.type == "private"

    if not private:
        await _delete_group_press(update)

    if text == "🎮 سرگرمی":
        await context.bot.send_message(update.effective_chat.id, "🎮 سرگرمی و بازی", reply_markup=get_entertainment_menu())
    elif text == "🛠 کاربردی":
        await context.bot.send_message(update.effective_chat.id, "🛠 ابزارهای کاربردی", reply_markup=get_utility_menu())
    elif text == "👤 حساب کاربری":
        await context.bot.send_message(update.effective_chat.id, "👤 حساب کاربری", reply_markup=get_user_menu())
    elif text == "🏦 بانک و اقتصاد":
        await context.bot.send_message(update.effective_chat.id, "🏦 بانک و اقتصاد", reply_markup=get_economy_menu())
    elif text == "🛡 مدیریت":
        if private:
            await context.bot.send_message(update.effective_chat.id, "🛡 مدیریت فقط داخل گروه قابل استفاده است.", reply_markup=get_main_menu())
        elif await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "🛡 منوی مدیریت", reply_markup=get_admin_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ این بخش مخصوص مدیران گروه است.", reply_markup=get_main_menu())
    elif text == "⚙️ تنظیمات":
        if private:
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات", reply_markup=get_settings_menu())
        elif await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات ربات در این گروه", reply_markup=get_settings_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "❌ فقط مدیران می‌توانند تنظیمات را تغییر دهند.", reply_markup=get_main_menu())
    elif text == "🤖 دستیار هوشمند":
        msg = "🤖 همین‌جا هر سوالی داری بپرس." if private else "🤖 در گروه من را با «سکتور» صدا بزن، منشن کن یا روی پیامم ریپلای کن."
        await context.bot.send_message(update.effective_chat.id, msg, reply_markup=get_main_menu())
    elif text in ("🤖 سکتور کوچولو","سکتور کوچولو"):
        if private:
            markup=InlineKeyboardMarkup([[InlineKeyboardButton("مراقبت در چت",callback_data="sector_pet",style="primary")],[InlineKeyboardButton("نسخه کامل مینی‌اپ",web_app=WebAppInfo(url=MINI_APP_URL),style="success")],[InlineKeyboardButton("ورود مستقیم امن",url=create_launch_url(update.effective_user.id),style="primary")]])
        else:
            markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 باز کردن در چت خصوصی",url="https://t.me/iSectorlandbot?start=miniapp")]])
        await context.bot.send_message(update.effective_chat.id,"🤖 سکتور کوچولو همراه دیجیتال توئه؛ با سکه، مأموریت، بازی و تمرین کمکش کن رشد کنه و به سکتور همه‌چیزدان تبدیل بشه!",reply_markup=markup)
    elif text == "🤝 پشتیبانی":
        await context.bot.send_message(update.effective_chat.id, "🤝 پشتیبانی: @sector_ad", reply_markup=get_main_menu())
    elif text in ("🔒 قفل‌های گروه", "🔒 قفل‌ها"):
        if not private and await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "🔐 مدیریت قفل‌ها", reply_markup=get_locks_menu())
    elif text == "👤 مدیریت اعضا":
        if not private and await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "👤 مدیریت اعضا", reply_markup=get_member_mgmt_menu())
    elif text == "⚙️ تنظیمات گروه":
        if not private and await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "⚙️ تنظیمات گروه", reply_markup=get_group_settings_menu())
    elif text == "👋 خوشامدگویی":
        if not private and await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "👋 تنظیمات خوشامدگویی", reply_markup=get_welcome_settings_menu())
    elif text == "📜 قوانین":
        if not private and await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "📜 تنظیمات قوانین", reply_markup=get_rules_settings_menu())
        elif private:
            await context.bot.send_message(update.effective_chat.id, "📜 قوانین فقط برای گروه کاربرد دارد.", reply_markup=get_main_menu())
    elif text == "🔙 بازگشت به مدیریت":
        if not private and await is_admin(update, context):
            await context.bot.send_message(update.effective_chat.id, "🛡 منوی مدیریت", reply_markup=get_admin_menu())
    elif text in ("🔙 بازگشت به منوی اصلی", "🔙 بازگشت به سرگرمی"):
        if text == "🔙 بازگشت به سرگرمی":
            await context.bot.send_message(update.effective_chat.id, "🎮 سرگرمی و بازی", reply_markup=get_entertainment_menu())
        else:
            await context.bot.send_message(update.effective_chat.id, "🏠 منوی اصلی SectorBot", reply_markup=get_main_menu())
    else:
        return

    raise ApplicationHandlerStop()


def get_panel_handlers():
    nav_regex = (
        "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🛠 کاربردی|⚙️ تنظیمات|🤖 دستیار هوشمند|🤖 سکتور کوچولو|سکتور کوچولو|🤝 پشتیبانی|"
        "🔒 قفل‌های گروه|🔒 قفل‌ها|👤 مدیریت اعضا|⚙️ تنظیمات گروه|👋 خوشامدگویی|📜 قوانین|"
        "🔙 بازگشت به مدیریت|🔙 بازگشت به منوی اصلی|🔙 بازگشت به سرگرمی)$"
    )
    return [
        CommandHandler("panel", panel_cmd),
        MessageHandler(filters.TEXT & filters.Regex(nav_regex), menu_navigation_handler),
    ]
