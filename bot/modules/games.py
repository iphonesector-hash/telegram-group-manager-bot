import random
import asyncio
import time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_ai_response, get_sector_prompt

# game_states[chat_id] = { "type": "game_type", "user_id": 123, "data": {}, "players": [] }
game_states = {}

async def games_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.utils.keyboards import get_games_menu
    await update.effective_message.reply_text("🎮 به بخش بازی‌های سکتور خوش اومدی!\nیکی رو انتخاب کن و شروع کنیم:", reply_markup=get_games_menu())
    raise ApplicationHandlerStop()

async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_dice()
    raise ApplicationHandlerStop()

async def coin_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice(["شیر 🦁", "خط 📏"])
    await update.effective_message.reply_text(f"🪙 سکه انداخته شد:\n\nنتیجه: {res}")
    raise ApplicationHandlerStop()

# --- Number Guess Game ---
async def start_number_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    target = random.randint(1, 100)
    game_states[chat_id] = {
        "type": "number_guess",
        "target": target,
        "attempts": 0,
        "max_attempts": 7,
        "user_id": update.effective_user.id
    }
    await update.effective_message.reply_text(
        "🎯 بازی حدس عدد شروع شد!\nمن یک عدد بین ۱ تا ۱۰۰ انتخاب کردم. ۷ فرصت داری تا حدسش بزنی.\n\nعدد مورد نظرت رو بفرست:"
    )
    raise ApplicationHandlerStop()

async def handle_number_guess(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    text = update.effective_message.text
    if not text.isdigit():
        return

    guess = int(text)
    state["attempts"] += 1
    chat_id = update.effective_chat.id

    if guess == state["target"]:
        await update.effective_message.reply_text(f"🎉 تبریک! درست بود.\nعدد من {guess} بود. توی {state['attempts']} مرحله برنده شدی! ✅")
        del game_states[chat_id]
    elif state["attempts"] >= state["max_attempts"]:
        await update.effective_message.reply_text(f"💀 باختی! فرصت‌هات تموم شد.\nعدد من {state['target']} بود. ❌")
        del game_states[chat_id]
    elif guess < state["target"]:
        await update.effective_message.reply_text(f"📈 بزرگتر! (فرصت باقی‌مانده: {state['max_attempts'] - state['attempts']})")
    else:
        await update.effective_message.reply_text(f"📉 کوچکتر! (فرصت باقی‌مانده: {state['max_attempts'] - state['attempts']})")
    raise ApplicationHandlerStop()

# --- Word Guess Game ---
async def start_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = ["سکتور", "تلگرام", "برنامه", "پایتون", "هوشمند", "سرگرمی", "فرمانده", "ایران", "تکنولوژی", "دیجیتال"]
    word = random.choice(words)
    chat_id = update.effective_chat.id

    # Create scrambled word
    scrambled = list(word)
    random.shuffle(scrambled)
    scrambled = "".join(scrambled)

    game_states[chat_id] = {
        "type": "word_guess",
        "word": word,
        "scrambled": scrambled,
        "user_id": update.effective_user.id
    }
    await update.effective_message.reply_text(
        f"📝 بازی حدس کلمه!\nحروف این کلمه رو به هم ریختم:\n\n`{scrambled}`\n\nکلمه درست چیه؟"
    )
    raise ApplicationHandlerStop()

async def handle_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    text = update.effective_message.text.strip()
    if text == state["word"]:
        await update.effective_message.reply_text(f"✅ آفرین! درست بود. کلمه مورد نظر '{state['word']}' بود. 🏆")
        del game_states[update.effective_chat.id]
        raise ApplicationHandlerStop()
    elif text == "راهنمایی":
        await update.effective_message.reply_text(f"💡 راهنمایی: حرف اول کلمه '{state['word'][0]}' هست.")
        raise ApplicationHandlerStop()

# --- Flag Guess Game ---
async def start_flag_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flags = {
        "🇮🇷": "ایران", "🇫🇷": "فرانسه", "🇩🇪": "آلمان", "🇯🇵": "ژاپن",
        "🇧🇷": "برزیل", "🇨🇦": "کانادا", "🇮🇹": "ایتالیا", "🇪سپانیا": "اسپانیا",
        "🇦🇷": "آرژانتین", "🇰🇷": "کره جنوبی"
    }
    flag, country = random.choice(list(flags.items()))
    chat_id = update.effective_chat.id
    game_states[chat_id] = {
        "type": "flag_guess",
        "country": country,
        "user_id": update.effective_user.id
    }
    await update.effective_message.reply_text(f"🚩 این پرچم کدوم کشوره؟\n\n{flag}")
    raise ApplicationHandlerStop()

async def handle_flag_guess(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    text = update.effective_message.text.strip()
    if text == state["country"]:
        await update.effective_message.reply_text(f"✅ درسته! این پرچم کشور {state['country']} بود. 🌟")
        del game_states[update.effective_chat.id]
        raise ApplicationHandlerStop()

# --- Rock Paper Scissors ---
async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text == "✂️ سنگ کاغذ قیچی":
        await update.effective_message.reply_text("✂️ یکی رو انتخاب کن: سنگ، کاغذ یا قیچی؟")
        raise ApplicationHandlerStop()

    user_choice = text.replace("✂️", "").strip()
    if user_choice not in ["سنگ", "کاغذ", "قیچی"]:
        return

    choices = ["سنگ", "کاغذ", "قیچی"]
    bot_choice = random.choice(choices)

    result = ""
    if user_choice == bot_choice:
        result = "🤝 مساوی شدیم!"
    elif (user_choice == "سنگ" and bot_choice == "قیچی") or \
         (user_choice == "کاغذ" and bot_choice == "سنگ") or \
         (user_choice == "قیچی" and bot_choice == "کاغذ"):
        result = "🎉 تو برنده شدی! ایول."
    else:
        result = "😜 من بردم! سکتور همیشه برنده‌ست."

    emojis = {"سنگ": "🪨", "کاغذ": "📄", "قیچی": "✂️"}
    await update.effective_message.reply_text(
        f"👤 انتخاب تو: {user_choice} {emojis[user_choice]}\n"
        f"🤖 انتخاب من: {bot_choice} {emojis[bot_choice]}\n\n"
        f"{result}"
    )
    raise ApplicationHandlerStop()

# --- Duel Game ---
async def start_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.effective_message.reply_text("⚔️ برای دوئل باید روی پیام رقیب خود ریپلای کنید و بنویسید: دوئل")
        raise ApplicationHandlerStop()

    player1 = update.effective_user
    player2 = update.message.reply_to_message.from_user

    if player1.id == player2.id:
        await update.effective_message.reply_text("❌ نمی‌تونی با خودت دوئل کنی!")
        raise ApplicationHandlerStop()

    await update.effective_message.reply_text(
        f"⚔️ چالش دوئل پذیرفته شد!\n\n"
        f"👤 {player1.mention_html()} VS {player2.mention_html()} 👤\n\n"
        "آماده باشید... ۳... ۲... ۱...",
        parse_mode="HTML"
    )
    await asyncio.sleep(2)

    winner = random.choice([player1, player2])
    loser = player2 if winner.id == player1.id else player1

    weapons = ["با شمشیر", "با هفت‌تیر", "با جادو", "با کلمات کنایه‌آمیز سکتور"]
    weapon = random.choice(weapons)

    await update.effective_message.reply_text(
        f"💥 شلیک نهایی!\n\n"
        f"🏆 {winner.mention_html()} موفق شد {loser.mention_html()} رو {weapon} شکست بده! 🏅",
        parse_mode="HTML"
    )
    raise ApplicationHandlerStop()

# --- Advanced Games (AI Powered) ---
async def intelligence_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک سوال تست هوش کوتاه و جالب به زبان فارسی بگو. خروجی: سوال: [متن] | پاسخ: [متن]"
    res = await get_ai_response(persona, prompt)
    if res and "|" in res:
        parts = res.split("|")
        q = parts[0].replace("سوال:", "").strip()
        a = parts[1].replace("پاسخ:", "").strip()
        chat_id = update.effective_chat.id
        game_states[chat_id] = {"type": "intel_test", "answer": a}
        await update.effective_message.reply_text(f"🧠 **تست هوش سکتور:**\n\n{q}\n\n💡 برای دیدن جواب بنویسید: جوابش")
    else:
        await update.effective_message.reply_text("❌ مغزم فعلاً برای تست هوش یاری نمی‌کنه!")
    raise ApplicationHandlerStop()

async def logic_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک معمای منطقی (Logic Puzzle) جذاب بگو. خروجی: معما: [متن] | پاسخ: [متن]"
    res = await get_ai_response(persona, prompt)
    if res and "|" in res:
        parts = res.split("|")
        q = parts[0].replace("معما:", "").strip()
        a = parts[1].replace("پاسخ:", "").strip()
        chat_id = update.effective_chat.id
        game_states[chat_id] = {"type": "logic_riddle", "answer": a}
        await update.effective_message.reply_text(f"🧩 **معمای منطقی:**\n\n{q}\n\n💡 برای دیدن جواب بنویسید: جوابش")
    else:
        await update.effective_message.reply_text("❌ فعلاً معمایی به ذهنم نمی‌رسه!")
    raise ApplicationHandlerStop()

async def daily_lucky_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Daily luck doesn't need state, just random result based on date and user_id
    user_id = update.effective_user.id
    today = datetime.date.today().isoformat()
    random.seed(f"{user_id}-{today}")
    score = random.randint(1, 100)

    if score > 90: res = "🌟 فوق‌العاده! امروز شانس با توئه."
    elif score > 70: res = "😊 خوبه، امروز روز بدی نیست."
    elif score > 40: res = "😐 معمولی، اتفاق خاصی نمی‌افته."
    else: res = "😅 مواظب باش، امروز زیاد رو شانس نیستی!"

    await update.effective_message.reply_text(f"🎲 **میزان شانس امروز شما:** {score}%\n\n{res}")
    random.seed() # reset seed
    raise ApplicationHandlerStop()

async def speed_contest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text_to_type = random.choice(["سکتور بهترین ربات تلگرامه", "من عاشق بازی‌های سکتورلند هستم", "برنامه‌نویسی با پایتون خیلی لذت‌بخشه"])

    await update.effective_message.reply_text(
        f"🏆 **مسابقه سرعت پاسخ**\n\nهر کی زودتر این جمله رو دقیقاً کپی کنه و بفرسته برنده است:\n\n`{text_to_type}`",
        parse_mode="Markdown"
    )
    game_states[chat_id] = {"type": "speed_contest", "text": text_to_type, "start_time": time.time()}
    raise ApplicationHandlerStop()

# --- Global Input Handler for Games ---
async def game_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in game_states:
        return

    state = game_states[chat_id]
    text = update.effective_message.text.strip()

    if text == "🔙 انصراف از بازی":
        del game_states[chat_id]
        await update.effective_message.reply_text("❌ بازی لغو شد.")
        raise ApplicationHandlerStop()

    if state["type"] == "number_guess":
        await handle_number_guess(update, context, state)
    elif state["type"] == "word_guess":
        await handle_word_guess(update, context, state)
    elif state["type"] == "flag_guess":
        await handle_flag_guess(update, context, state)
    elif state["type"] in ["intel_test", "logic_riddle"] and text == "جوابش":
        await update.effective_message.reply_text(f"✅ پاسخ:\n\n{state['answer']}")
        del game_states[chat_id]
        raise ApplicationHandlerStop()
    elif state["type"] == "speed_contest":
        if text == state["text"]:
            elapsed = round(time.time() - state["start_time"], 2)
            await update.effective_message.reply_text(f"🎉 تبریک {update.effective_user.mention_html()}! تو زودتر از همه فرستادی. ✅\n⏱ زمان: {elapsed} ثانیه", parse_mode="HTML")
            del game_states[chat_id]
            raise ApplicationHandlerStop()

def get_handlers():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^🎮 بازی‌ها$"), games_menu_handler),
        MessageHandler(filters.TEXT & filters.Regex("^🎲 تاس$"), dice_game),
        MessageHandler(filters.TEXT & filters.Regex("^🪙 پرتاب سکه$"), coin_game),
        MessageHandler(filters.TEXT & filters.Regex("^🔢 حدس عدد$"), start_number_guess),
        MessageHandler(filters.TEXT & filters.Regex("^📝 حدس کلمه$"), start_word_guess),
        MessageHandler(filters.TEXT & filters.Regex("^🚩 حدس پرچم$"), start_flag_guess),
        MessageHandler(filters.TEXT & filters.Regex("^(✂️ سنگ کاغذ قیچی|سنگ|کاغذ|قیچی)$"), rps_game),
        MessageHandler(filters.TEXT & filters.Regex("^⚔️ دوئل$"), start_duel),
        MessageHandler(filters.TEXT & filters.Regex("^🧠 تست هوش$"), intelligence_test),
        MessageHandler(filters.TEXT & filters.Regex("^🧩 معمای منطقی$"), logic_riddle),
        MessageHandler(filters.TEXT & filters.Regex("^🎲 بازی شانسی روزانه$"), daily_lucky_game),
        MessageHandler(filters.TEXT & filters.Regex("^🏆 مسابقه سرعت پاسخ$"), speed_contest),
        # Pass-through for active games
        MessageHandler(filters.TEXT & ~filters.COMMAND, game_input_handler),
    ]
