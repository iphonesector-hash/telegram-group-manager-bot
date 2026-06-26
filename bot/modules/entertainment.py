import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_ai_response, get_new_joke as get_ai_joke, get_new_riddle as get_ai_riddle, get_new_fact, get_motivation, hafez_fortune
from bot.utils.keyboards import get_games_menu, get_tod_menu, get_joke_categories_menu, get_challenge_categories_menu

# Last riddle answers memory
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
    prompt = "یک داستان کوتاه خلاقانه و جدید به زبان فارسی بنویس. داستان باید حداقل دو پاراگراف باشد و موضوعی جذاب داشته باشد."
    res = await get_ai_response(prompt, "یک داستان بگو")
    fallback = "📖 روزی روزگاری در دنیای دیجیتال، رباتی به نام سکتور زندگی می‌کرد که به دنبال کشف اسرار کدها بود..."
    await update.effective_message.reply_text(res or fallback, parse_mode=None)
    raise ApplicationHandlerStop()

async def get_riddle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    # Prompting for answer separately to store it
    prompt = "یک معمای منطقی جدید به همراه پاسخ به زبان فارسی بگو. فرمت خروجی: معما: [متن] | پاسخ: [پاسخ]"
    res = await get_ai_response(prompt, "معما بگو")

    if res and "|" in res:
        parts = res.split("|")
        riddle = parts[0].replace("معما:", "").strip()
        answer = parts[1].replace("پاسخ:", "").strip()
        riddle_answers[update.effective_chat.id] = answer
        await update.effective_message.reply_text(f"❓ {riddle}\n\n💡 برای دیدن جواب بنویسید: جواب معما", parse_mode=None)
    else:
        await get_ai_riddle(update, context) # Fallback to original
    raise ApplicationHandlerStop()

async def reveal_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in riddle_answers:
        await update.effective_message.reply_text(f"✅ پاسخ معما: {riddle_answers[chat_id]}", parse_mode=None)
        del riddle_answers[chat_id]
    else:
        await update.effective_message.reply_text("❌ معمایی در حافظه یافت نشد. ابتدا یک معما بگیرید.")
    raise ApplicationHandlerStop()

async def get_categorized_joke(update: Update, category):
    await update.effective_message.reply_chat_action("typing")
    prompt = f"یک جوک جدید و خنده‌دار در دسته '{category}' به زبان فارسی بگو. جوک باید با مفهوم و شنیدنی باشد."
    res = await get_ai_response(prompt, f"جوک {category} بگو")
    await update.effective_message.reply_text(res or "😂 فعلاً جوکی یادم نمیاد!", parse_mode=None)

async def get_tod_action(update: Update, type):
    await update.effective_message.reply_chat_action("typing")
    if type == "truth":
        prompt = "یک سوال جرات و حقیقت در بخش 'حقیقت' بپرس. سوال باید خلاقانه، دوستانه و کمی چالش‌برانگیز باشد."
        title = "💬 حقیقت"
    elif type == "dare":
        prompt = "یک چالش 'جرات' برای بازی جرات و حقیقت در گروه تلگرامی بگو. چالش باید امن، خنده‌دار و قابل انجام باشد."
        title = "🎯 جرات"
    else:
        # Random
        return await get_tod_action(update, random.choice(["truth", "dare"]))

    res = await get_ai_response(prompt, f"بازی {title}")
    await update.effective_message.reply_text(f"🎭 **بازی جرات و حقیقت**\n\n{title}:\n{res}", parse_mode=None)

async def get_categorized_challenge(update: Update, category):
    await update.effective_message.reply_chat_action("typing")
    prompt = f"یک چالش جدید در دسته '{category}' بگو. چالش باید جذاب باشد."
    res = await get_ai_response(prompt, f"چالش {category}")
    await update.effective_message.reply_text(f"🎯 **چالش سکتور ({category})**\n\n{res}", parse_mode=None)

async def ent_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text

    if text == "😂 جوک":
        await update.effective_message.reply_text("🤣 دسته جوک مورد نظر را انتخاب کنید:", reply_markup=get_joke_categories_menu())
    elif text in ["😂 خنده‌دار", "😈 شیطنتی", "🧠 هوشمندانه", "🤣 کوتاه"]:
        await get_categorized_joke(update, text)

    elif text == "💡 دانستنی":
        await get_new_fact(update, context)
    elif text == "❓ معما":
        await get_riddle_cmd(update, context)
    elif text == "📖 داستان":
        await get_story_cmd(update, context)
    elif text == "🎲 تاس":
        await dice_cmd(update, context)
    elif text == "🪙 پرتاب سکه":
        await coin_cmd(update, context)
    elif text == "🎯 چالش":
        await update.effective_message.reply_text("🎯 نوع چالش را انتخاب کنید:", reply_markup=get_challenge_categories_menu())
    elif text in ["🎯 چالش تصادفی", "⚡ چالش سخت", "😂 چالش خنده‌دار", "🧠 چالش ذهنی"]:
        await get_categorized_challenge(update, text)

    elif text == "📜 فال حافظ":
        await hafez_fortune(update, context)
    elif text == "🎮 بازی‌ها":
        await update.effective_message.reply_text("🎮 منوی بازی‌ها باز شد:", reply_markup=get_games_menu())
    elif text == "🎭 جرات و حقیقت":
        await update.effective_message.reply_text("🎭 آماده بازی هستی؟", reply_markup=get_tod_menu())
    elif text == "🎯 جرات":
        await get_tod_action(update, "dare")
    elif text == "💬 حقیقت":
        await get_tod_action(update, "truth")
    elif text == "🎲 تصادفی":
        await get_tod_action(update, "random")
    else:
        return
    raise ApplicationHandlerStop()

def get_handlers():
    reveal_regex = "^(جواب معما|جوابش؟)$"
    ent_regex = "^(😂 جوک|💡 دانستنی|❓ معما|📖 داستان|🎲 تاس|🪙 پرتاب سکه|🎯 چالش|📜 فال حافظ|🎮 بازی‌ها|🎭 جرات و حقیقت|😂 خنده‌دار|😈 شیطنتی|🧠 هوشمندانه|🤣 کوتاه|🎯 جرات|💬 حقیقت|🎲 تصادفی|🎯 چالش تصادفی|⚡ چالش سخت|😂 چالش خنده‌دار|🧠 چالش ذهنی)$"
    return [
        CommandHandler("joke", get_ai_joke),
        CommandHandler("fact", get_new_fact),
        CommandHandler("riddle", get_riddle_cmd),
        CommandHandler("dice", dice_cmd),
        CommandHandler("coin", coin_cmd),
        CommandHandler("story", get_story_cmd),
        MessageHandler(filters.TEXT & filters.Regex(reveal_regex), reveal_riddle_answer),
        MessageHandler(filters.TEXT & filters.Regex(ent_regex), ent_button_handler),
    ]
