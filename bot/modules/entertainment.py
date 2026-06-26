import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_ai_response, get_new_joke as get_ai_joke, get_new_riddle as get_ai_riddle, get_new_fact, get_motivation, hafez_fortune
from bot.utils.keyboards import get_games_menu, get_tod_menu, get_joke_categories_menu, get_challenge_categories_menu

riddle_answers = {}

async def dice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message:
        await update.effective_message.reply_dice()
    raise ApplicationHandlerStop()

async def coin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice(["شیر 🦁", "خط 📏"])
    await update.effective_message.reply_text(f"🪙 سکه انداخته شد:\n\nنتیجه: {res}", parse_mode=None)
    raise ApplicationHandlerStop()

async def get_story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    prompt = "یک داستان کوتاه خلاقانه و جدید به زبان فارسی بنویس. داستان باید حداقل سه پاراگراف باشد و موضوعی جذاب داشته باشد. موضوع می‌تواند علمی-تخیلی یا فانتزی باشد."
    res = await get_ai_response(prompt, "یک داستان بگو")
    await update.effective_message.reply_text(res or "📖 متأسفانه کتاب داستانم فعلاً گم شده!", parse_mode=None)
    raise ApplicationHandlerStop()

async def get_riddle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    prompt = "یک معمای کوتاه و باحال به زبان فارسی بگو. فرمت خروجی دقیقا این باشد: معما: [متن] | پاسخ: [پاسخ]"
    res = await get_ai_response(prompt, "معما بگو")

    if res and "|" in res:
        parts = res.split("|")
        riddle = parts[0].replace("معما:", "").strip()
        answer = parts[1].replace("پاسخ:", "").strip()
        riddle_answers[update.effective_chat.id] = answer
        await update.effective_message.reply_text(f"❓ {riddle}\n\n💡 برای دیدن جواب بنویسید: جواب معما یا جوابش؟", parse_mode=None)
    else:
        await get_ai_riddle(update, context)
    raise ApplicationHandlerStop()

async def reveal_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in riddle_answers:
        await update.effective_message.reply_text(f"✅ پاسخ معما:\n\n{riddle_answers[chat_id]}", parse_mode=None)
        del riddle_answers[chat_id]
    else:
        await update.effective_message.reply_text("❌ معمایی فعال نیست. ابتدا یک معما بگیرید.")
    raise ApplicationHandlerStop()

async def get_categorized_joke(update: Update, category):
    await update.effective_message.reply_chat_action("typing")
    prompt = f"یک جوک کوتاه (حداکثر ۴ خط) و خیلی خنده‌دار در دسته '{category}' به زبان فارسی بگو. اصلا رسمی نباش."
    res = await get_ai_response(prompt, f"جوک {category} بگو")
    await update.effective_message.reply_text(res or "😂 جوکم نمیاد فعلاً!", parse_mode=None)

async def get_tod_action(update: Update, mode):
    await update.effective_message.reply_chat_action("typing")
    if mode == "truth":
        prompt = "یک سوال جالب برای بازی 'حقیقت' بپرس."
        title = "💬 حقیقت"
    elif mode == "dare":
        prompt = "یک چالش 'جرات' جالب و امن برای گروه تلگرامی بگو."
        title = "🎯 جرات"
    else:
        return await get_tod_action(update, random.choice(["truth", "dare"]))

    res = await get_ai_response(prompt, f"بازی {title}")
    await update.effective_message.reply_text(f"🎭 **بازی جرات و حقیقت**\n\n{title}:\n{res}", parse_mode=None)

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choices = ["سنگ 🪨", "کاغذ 📄", "قیچی ✂️"]
    bot_choice = random.choice(choices)
    await update.effective_message.reply_text(f"🎮 من انتخاب کردم: {bot_choice}\n\nحالا نوبت توئه! سنگ، کاغذ یا قیچی؟", parse_mode=None)
    raise ApplicationHandlerStop()

async def ent_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text

    if text == "😂 جوک":
        await update.effective_message.reply_text("🤣 دسته جوک:", reply_markup=get_joke_categories_menu())
    elif text in ["😂 خنده‌دار", "😈 شیطنتی", "🧠 هوشمندانه", "🤣 کوتاه"]:
        await get_categorized_joke(update, text)
    elif text == "❓ معما":
        await get_riddle_cmd(update, context)
    elif text == "📖 داستان":
        await get_story_cmd(update, context)
    elif text == "🎯 چالش":
        await update.effective_message.reply_text("🎯 نوع چالش:", reply_markup=get_challenge_categories_menu())
    elif text in ["🎯 چالش تصادفی", "⚡ چالش سخت", "😂 چالش خنده‌دار", "🧠 چالش ذهنی"]:
        await get_tod_action(update, "dare") # simplified
    elif text == "🎭 جرات و حقیقت":
        await update.effective_message.reply_text("🎭 جرات یا حقیقت؟", reply_markup=get_tod_menu())
    elif text == "🎯 جرات":
        await get_tod_action(update, "dare")
    elif text == "💬 حقیقت":
        await get_tod_action(update, "truth")
    elif text == "🎲 تصادفی":
        await get_tod_action(update, "random")
    elif text == "💡 دانستنی":
        await get_new_fact(update, context)
    elif text == "📜 فال حافظ":
        await hafez_fortune(update, context)
    elif text == "🎮 بازی‌ها":
        await update.effective_message.reply_text("🎮 منوی بازی‌ها:", reply_markup=get_games_menu())
    else:
        return
    raise ApplicationHandlerStop()

def get_handlers():
    return [
        CommandHandler("riddle", get_riddle_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(جواب معما|جوابش؟)$"), reveal_riddle_answer),
        MessageHandler(filters.TEXT & filters.Regex("^(😂 جوک|💡 دانستنی|❓ معما|📖 داستان|🎲 تاس|🪙 پرتاب سکه|🎯 چالش|📜 فال حافظ|🎮 بازی‌ها|🎭 جرات و حقیقت|😂 خنده‌دار|😈 شیطنتی|🧠 هوشمندانه|🤣 کوتاه|🎯 جرات|💬 حقیقت|🎲 تصادفی|🎯 چالش تصادفی|⚡ چالش سخت|😂 چالش خنده‌دار|🧠 چالش ذهنی)$"), ent_button_handler),
    ]
