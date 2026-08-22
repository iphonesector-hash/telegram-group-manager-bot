import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://mini-app-sector.vercel.app")


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
            [InlineKeyboardButton("🚀 باز کردن SectorLand Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 باز کردن SectorLand Mini App", url=MINI_APP_URL)]
        ])

    await update.effective_message.reply_text(
        "🌐 به iSectorLand خوش اومدی ✨\n\n"
        "از اینجا می‌تونی وارد مینی‌اپ بشی و امکانات حساب، اقتصاد و مدیریت SectorLand رو باز کنی.\n\n"
        "💡 در چت خصوصی، دکمه مینی‌اپ به منوی پایین تلگرام هم اضافه می‌شه.",
        reply_markup=keyboard,
    )
    raise ApplicationHandlerStop()


start_handler = CommandHandler(["start", "miniapp"], start)
