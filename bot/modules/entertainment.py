import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_new_joke, get_new_riddle, get_new_fact, get_motivation, hafez_fortune

async def dice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message:
        await update.effective_message.reply_dice()
    raise ApplicationHandlerStop()

async def coin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice(["شیر 🦁", "خط 📏"])
    await update.effective_message.reply_text(f"🪙 سکه انداخته شد:\n\nنتیجه: **{res}**", parse_mode="Markdown")
    raise ApplicationHandlerStop()

async def challenge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    challenges = [
        "همین الان ۳ بار بلند بگو: «چای داغ، دایی چاق»! 🍵",
        "نام ۵ شهر ایران که با حرف «س» شروع می‌شوند را بگو. 🗺",
        "یک سلفی خنده‌دار بگیر و تو گروه بفرست! 📸",
        "اسم یک فیلم رو با ایموجی بنویس بقیه حدس بزنن. 🎭"
    ]
    await update.effective_message.reply_text(f"🎯 **چالش سکتور:**\n\n{random.choice(challenges)}", parse_mode="Markdown")
    raise ApplicationHandlerStop()

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choices = ["سنگ 🪨", "کاغذ 📄", "قیچی ✂️"]
    bot_choice = random.choice(choices)
    await update.effective_message.reply_text(f"🎮 من انتخاب کردم: **{bot_choice}**\n\nحالا نوبت توئه! سنگ، کاغذ یا قیچی؟", parse_mode="Markdown")
    raise ApplicationHandlerStop()

async def ent_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text == "😂 جوک":
        await get_new_joke(update, context)
    elif text == "💡 دانستنی":
        await get_new_fact(update, context)
    elif text == "❓ معما":
        await get_new_riddle(update, context)
    elif text == "📖 داستان":
        await update.effective_message.reply_text("📖 روزی روزگاری در قلمرو سکتور، رباتی متولد شد که هدفش نظم بخشیدن به گروه‌های تلگرامی بود...")
    elif text == "🎲 تاس":
        await dice_cmd(update, context)
    elif text == "🪙 پرتاب سکه":
        await coin_cmd(update, context)
    elif text == "🎯 چالش":
        await challenge_cmd(update, context)
    elif text == "📜 فال حافظ":
        await hafez_fortune(update, context)
    elif text == "🎮 بازی‌ها":
        from bot.utils.keyboards import get_games_menu
        await update.effective_message.reply_text("🎮 منوی بازی‌ها باز شد:", reply_markup=get_games_menu())
    else:
        return
    raise ApplicationHandlerStop()

def get_handlers():
    return [
        CommandHandler("joke", get_new_joke),
        CommandHandler("fact", get_new_fact),
        CommandHandler("riddle", get_new_riddle),
        CommandHandler("dice", dice_cmd),
        CommandHandler("coin", coin_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(😂 جوک|💡 دانستنی|❓ معما|📖 داستان|🎲 تاس|🪙 پرتاب سکه|🎯 چالش|📜 فال حافظ|🎮 بازی‌ها)$"), ent_button_handler),
    ]
