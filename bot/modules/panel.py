import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.database.session import get_session
from bot.database.models import Group
from bot.utils.helpers import is_admin

# --- Keyboards ---
def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["🛡 مدیریت", "👤 کاربر"],
        ["🏦 بانک", "🎮 سرگرمی"],
        ["🛠 کاربردی", "⚙️ تنظیمات"],
        ["🆘 پشتیبانی"]
    ], resize_keyboard=True)

def admin_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["🔒 قفل‌ها", "👋 خوش‌آمدگویی"],
        ["⚠️ هشدارها", "⚙️ تنظیمات گروه"],
        ["⬅️ برگشت"]
    ], resize_keyboard=True)

def user_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["👤 پروفایل", "🏆 رتبه‌بندی"],
        ["📜 قوانین", "⬅️ برگشت"]
    ], resize_keyboard=True)

def bank_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["💰 کیف پول", "🎁 جایزه روزانه"],
        ["🔄 انتقال سکه", "🏦 وام"],
        ["💳 پرداخت وام", "💎 ثروتمندترین‌ها"],
        ["⬅️ برگشت"]
    ], resize_keyboard=True)

def fun_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["😂 جوک", "📜 فال حافظ"],
        ["💡 فکت", "📝 متن"],
        ["🎲 تاس", "🪙 شیر یا خط"],
        ["❓ چیستان", "🎮 سنگ کاغذ قیچی"],
        ["🔡 حدس کلمه", "🏳️ حدس پرچم"],
        ["⚔️ دوئل", "👮 دزد و پلیس"],
        ["⬅️ برگشت"]
    ], resize_keyboard=True)

def tools_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["🌍 مترجم", "☁️ آب و هوا"],
        ["⚖️ تبدیل واحد", "🧮 حسابگر"],
        ["⬅️ برگشت"]
    ], resize_keyboard=True)

def settings_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["👋 خوش‌آمدگویی (تنظیم)", "🔒 قفل‌ها (تنظیم)"],
        ["🛡 ضداسپم", "📜 قوانین (تنظیم)"],
        ["⬅️ برگشت"]
    ], resize_keyboard=True)

# --- Handlers ---
async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "💎 **به منوی پیشرفته SectorBot خوش آمدید!**\nلطفاً از دکمه‌های زیر استفاده کنید:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    # 1. Main Menus
    if text == "🛡 مدیریت":
        if not await is_admin(update, context):
            await update.message.reply_text("❌ این بخش مخصوص ادمین‌ها است.")
            return
        await update.message.reply_text("🛡 **بخش مدیریت:**", reply_markup=admin_menu_keyboard())

    elif text == "👤 کاربر":
        await update.message.reply_text("👤 **بخش کاربری:**", reply_markup=user_menu_keyboard())

    elif text == "🏦 بانک":
        await update.message.reply_text("🏦 **بانک SectorBot:**", reply_markup=bank_menu_keyboard())

    elif text == "🎮 سرگرمی":
        await update.message.reply_text("🎮 **بخش سرگرمی:**", reply_markup=fun_menu_keyboard())

    elif text == "🛠 کاربردی":
        await update.message.reply_text("🛠 **بخش ابزارها:**", reply_markup=tools_menu_keyboard())

    elif text == "⚙️ تنظیمات":
        if not await is_admin(update, context):
            await update.message.reply_text("❌ دسترسی محدود به ادمین.")
            return
        await update.message.reply_text("⚙️ **تنظیمات ربات:**", reply_markup=settings_menu_keyboard())

    elif text == "🆘 پشتیبانی":
        keyboard = [[InlineKeyboardButton("💬 ارتباط با پشتیبانی", url="https://t.me/sector_ad")]]
        await update.message.reply_text("🆘 برای پشتیبانی مستقیم با ما در ارتباط باشید:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "⬅️ برگشت":
        await update.message.reply_text("💎 **منوی اصلی:**", reply_markup=main_menu_keyboard())

    # 2. Features Redirections
    # --- Management ---
    elif text == "🔒 قفل‌ها":
        from bot.modules.locks import locks_status_cmd
        await locks_status_cmd(update, context)
    elif text == "👋 خوش‌آمدگویی":
        await update.message.reply_text("🌟 از دستور `/welcome on/off` برای مدیریت خوش‌آمدگویی استفاده کنید.")
    elif text == "⚠️ هشدارها":
        await update.message.reply_text("👤 برای مدیریت هشدارها از دستور `/warns` (ریپلای) استفاده کنید.")
    elif text == "⚙️ تنظیمات گروه":
        await update.message.reply_text("⚙️ تنظیمات پیشرفته گروه فعال شد.", reply_markup=settings_menu_keyboard())

    # --- User ---
    elif text == "👤 پروفایل":
        from bot.modules.profile import profile_cmd
        await profile_cmd(update, context)
    elif text == "🏆 رتبه‌بندی":
        from bot.modules.profile import top_cmd
        await top_cmd(update, context)
    elif text == "📜 قوانین":
        from bot.modules.rules import rules_cmd
        await rules_cmd(update, context)

    # --- Bank ---
    elif text == "💰 کیف پول":
        from bot.modules.economy import coins_cmd
        await coins_cmd(update, context)
    elif text == "🎁 جایزه روزانه":
        from bot.modules.economy import daily_cmd
        await daily_cmd(update, context)
    elif text == "🔄 انتقال سکه":
        await update.message.reply_text("💸 برای انتقال سکه: `/transfer ID Amount`")
    elif text == "🏦 وام":
        from bot.modules.economy import loan_cmd
        await loan_cmd(update, context)
    elif text == "💳 پرداخت وام":
        from bot.modules.economy import repay_cmd
        await repay_cmd(update, context)
    elif text == "💎 ثروتمندترین‌ها":
        from bot.modules.economy import richest_cmd
        await richest_cmd(update, context)

    # --- Fun ---
    elif text == "😂 جوک":
        from bot.modules.entertainment import joke_cmd
        await joke_cmd(update, context)
    elif text == "📜 فال حافظ":
        from bot.modules.entertainment import hafez_cmd
        await hafez_cmd(update, context)
    elif text == "💡 فکت":
        from bot.modules.entertainment import fact_cmd
        await fact_cmd(update, context)
    elif text == "📝 متن":
        from bot.modules.entertainment import story_cmd
        await story_cmd(update, context)
    elif text == "🎲 تاس":
        from bot.modules.entertainment import dice_cmd
        await dice_cmd(update, context)
    elif text == "🪙 شیر یا خط":
        from bot.modules.entertainment import coin_cmd
        await coin_cmd(update, context)
    elif text == "❓ چیستان":
        from bot.modules.entertainment import riddle_cmd
        await riddle_cmd(update, context)
    elif text == "🎮 سنگ کاغذ قیچی":
        from bot.modules.entertainment import rps_cmd
        await rps_cmd(update, context)
    elif text == "🔡 حدس کلمه":
        from bot.modules.entertainment import guess_word_cmd
        await guess_word_cmd(update, context)
    elif text == "🏳️ حدس پرچم":
        from bot.modules.entertainment import guess_flag_cmd
        await guess_flag_cmd(update, context)
    elif text == "⚔️ دوئل":
        from bot.modules.entertainment import duel_cmd
        await duel_cmd(update, context)
    elif text == "👮 دزد و پلیس":
        from bot.modules.entertainment import cops_cmd
        await cops_cmd(update, context)

    # --- Tools ---
    elif text == "🌍 مترجم":
        from bot.modules.tools import translate_cmd
        await translate_cmd(update, context)
    elif text == "☁️ آب و هوا":
        from bot.modules.tools import weather_cmd
        await weather_cmd(update, context)
    elif text == "⚖️ تبدیل واحد":
        from bot.modules.tools import convert_cmd
        await convert_cmd(update, context)
    elif text == "🧮 حسابگر":
        from bot.modules.tools import calc_cmd
        await calc_cmd(update, context)

    # --- Group Settings ---
    elif text == "👋 خوش‌آمدگویی (تنظیم)":
        await update.message.reply_text("💡 برای تغییر متن خوش‌آمدگویی: `/setwelcome TEXT`")
    elif text == "🔒 قفل‌ها (تنظیم)":
        await update.message.reply_text("🔒 از دستور `/lock links/photos/...` استفاده کنید.")
    elif text == "🛡 ضداسپم":
        from bot.modules.antispam import antispam_toggle_cmd
        await antispam_toggle_cmd(update, context)
    elif text == "📜 قوانین (تنظیم)":
        await update.message.reply_text("📜 برای ثبت قوانین: `/setrules TEXT`")

def get_panel_handlers():
    buttons = [
        "🛡 مدیریت", "👤 کاربر", "🏦 بانک", "🎮 سرگرمی", "🛠 کاربردی", "⚙️ تنظیمات", "🆘 پشتیبانی", "⬅️ برگشت",
        "🔒 قفل‌ها", "👋 خوش‌آمدگویی", "⚠️ هشدارها", "⚙️ تنظیمات گروه",
        "👤 پروفایل", "🏆 رتبه‌بندی", "📜 قوانین",
        "💰 کیف پول", "🎁 جایزه روزانه", "🔄 انتقال سکه", "🏦 وام", "💳 پرداخت وام", "💎 ثروتمندترین‌ها",
        "😂 جوک", "📜 فال حافظ", "💡 فکت", "📝 متن", "🎲 تاس", "🪙 شیر یا خط", "❓ چیستان", "🎮 سنگ کاغذ قیچی", "🔡 حدس کلمه", "🏳️ حدس پرچم", "⚔️ دوئل", "👮 دزد و پلیس",
        "🌍 مترجم", "☁️ آب و هوا", "⚖️ تبدیل واحد", "🧮 حسابگر",
        "👋 خوش‌آمدگویی (تنظیم)", "🔒 قفل‌ها (تنظیم)", "🛡 ضداسپم", "📜 قوانین (تنظیم)"
    ]
    pattern = "^(" + "|".join(re.escape(b) for b in buttons) + ")$"
    nav_filters = filters.TEXT & filters.Regex(pattern)
    return [
        CommandHandler("panel", panel_cmd),
        MessageHandler(nav_filters, menu_navigation_handler),
    ]
