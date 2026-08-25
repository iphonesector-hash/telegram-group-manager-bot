import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop
from bot.utils.keyboards import get_main_menu
from bot.utils.animated_emoji import animated_emoji, get_sector_emoji_ids

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app").split("?", 1)[0]
BOT_DEEP_LINK = os.getenv("BOT_DEEP_LINK", "https://t.me/iSectorlandbot?start=miniapp")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    is_private = bool(chat and chat.type == "private")
    icons = get_sector_emoji_ids()
    icon = lambda n: icons[n % len(icons)] if icons else None

    if is_private:
        try:
            await context.bot.set_chat_menu_button(
                chat_id=chat.id,
                menu_button=MenuButtonWebApp(
                    text="sector",
                    web_app=WebAppInfo(url=MINI_APP_URL),
                ),
            )
        except Exception as e:
            print(f"Mini App menu button error: {e}")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("سکتور کوچولو", callback_data="sector_pet", style="primary", icon_custom_emoji_id=icon(0)),
             InlineKeyboardButton("sector", web_app=WebAppInfo(url=MINI_APP_URL), icon_custom_emoji_id=icon(1))]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("سکتور کوچولو", url="https://t.me/iSectorlandbot?start=sector", icon_custom_emoji_id=icon(0))],
            [InlineKeyboardButton("باز کردن Mini App در چت خصوصی", url=BOT_DEEP_LINK, icon_custom_emoji_id=icon(1))]
        ])

    globe = animated_emoji(2, "🌐")
    sparkle = animated_emoji(3, "✨")
    tip = animated_emoji(4, "💡")
    await update.effective_message.reply_text(
        f"{globe} <b>به iSectorLand خوش اومدی</b> {sparkle}\n\n"
        "از اینجا می‌تونی وارد مینی‌اپ مدیریت ربات بشی و امکانات حساب، اقتصاد، بازی‌ها و SectorLand رو باز کنی.\n\n"
        f"{tip} برای همگام‌سازی امن حساب، Mini App را از دکمه Web App داخل چت خصوصی ربات باز کن.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    if is_private:
        home = animated_emoji(5, "🏠")
        await update.effective_message.reply_text(
            f"{home} <b>منوی اصلی آماده است</b>؛ یکی از دکمه‌های پایین چت را انتخاب کن.",
            parse_mode="HTML",
            reply_markup=get_main_menu(),
        )
    raise ApplicationHandlerStop()


start_handler = CommandHandler(["start", "miniapp"], start)
