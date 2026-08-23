import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop
from bot.services.miniapp_launch import create_launch_url

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0] + "?v=20260823-3"
BOT_DEEP_LINK = os.getenv("BOT_DEEP_LINK", "https://t.me/iSectorlandbot?start=miniapp")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    is_private = bool(chat and chat.type == "private")

    if is_private:
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat.id,
                menu_button=MenuButtonWebApp(
                    text="🚀 مینی اپ SectorLand",
                    web_app=WebAppInfo(url=MINI_APP_URL),
                ),
            )
        except Exception as e:
            print(f"Mini App menu button error: {e}")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("سکتور کوچولوی من", callback_data="sector_pet", style="primary")],
            [InlineKeyboardButton("باز کردن SectorLand Mini App", web_app=WebAppInfo(url=MINI_APP_URL), style="success")],
            [InlineKeyboardButton("ورود مستقیم امن",url=create_launch_url(update.effective_user.id),style="primary")]
        ])
    else:
        # Telegram only provides trusted WebApp initData when the Mini App is
        # launched through a WebApp/Menu button in the user's private chat.
        # A raw https:// Mini App URL from a group can open without initData and
        # then every authenticated API call correctly fails with 401/403.
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 سکتور کوچولو", url="https://t.me/iSectorlandbot?start=sector")],
            [InlineKeyboardButton("🚀 باز کردن Mini App در چت خصوصی", url=BOT_DEEP_LINK)]
        ])

    await update.effective_message.reply_text(
        "🌐 به iSectorLand خوش اومدی ✨\n\n"
        "از اینجا می‌تونی وارد مینی‌اپ مدیریت خود ربات بشی و امکانات حساب، اقتصاد، بازی‌ها و مدیریت SectorLand رو باز کنی.\n\n"
        "💡 برای همگام‌سازی امن حساب، Mini App باید از دکمه Web App داخل چت خصوصی ربات باز شود.",
        reply_markup=keyboard,
    )
    raise ApplicationHandlerStop()


start_handler = CommandHandler(["start", "miniapp"], start)
