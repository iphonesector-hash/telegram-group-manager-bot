import random
import asyncio
import time
import datetime
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_ai_response, get_sector_prompt
from bot.database.session import get_session
from bot.database.models import User
from api.quiz_bank import QUIZ_BANK as CURATED_QUIZ_BANK, _FLAGS

# game_states is used by the older text games.
game_states = {}
# quiz_states[qid] = question metadata. answered is per-user, so group quizzes can be played by everyone once.
quiz_states = {}
from bot.services.runtime_state import delete_state, get_state, set_state

def _save_game(chat_id, state):
    game_states[chat_id] = state
    set_state("game", str(chat_id), state)

def _load_game(chat_id):
    return game_states.get(chat_id) or get_state("game", str(chat_id))

def _delete_game(chat_id):
    game_states.pop(chat_id, None)
    delete_state("game", str(chat_id))

QUIZ_BANK = {
    kind: [
        {"id": q["id"], "q": q["question"], "options": q["options"], "correct": q["answer"], "explain": q["explanation"]}
        for q in CURATED_QUIZ_BANK if q["kind"] == kind
    ]
    for kind in ("intel", "logic")
}


def _ensure_user(tg_user):
    session = get_session()
    user = session.query(User).filter(User.id == tg_user.id).first()
    if not user:
        user = User(id=tg_user.id, username=tg_user.username, first_name=tg_user.first_name or "", coins=0, xp=0, level=1)
        session.add(user)
        session.commit()
    return session, user


def _award_quiz(tg_user, coins=5, xp=10):
    session, user = _ensure_user(tg_user)
    user.coins = int(user.coins or 0) + coins
    user.xp = int(user.xp or 0) + xp
    # Simple deterministic level curve: each 100 XP advances one level.
    user.level = max(int(user.level or 1), int(user.xp or 0) // 100 + 1)
    session.commit()
    result = (user.coins, user.xp, user.level)
    session.close()
    return result


def _quiz_keyboard(qid, options):
    rows = []
    for i, option in enumerate(options):
        rows.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"quiz:{qid}:{i}")])
    return InlineKeyboardMarkup(rows)


async def _send_quiz(update, context, kind):
    recent_key = f"recent_quiz_{kind}"
    recent = list(context.user_data.get(recent_key, []))
    fresh = [item for item in QUIZ_BANK[kind] if item["id"] not in recent]
    if not fresh:
        recent = []
        fresh = QUIZ_BANK[kind]
    item = random.choice(fresh)
    context.user_data[recent_key] = (recent + [item["id"]])[-12:]
    qid = uuid.uuid4().hex[:10]
    quiz_states[qid] = {
        "kind": kind,
        "question": item["q"],
        "options": item["options"],
        "correct": item["correct"],
        "explain": item["explain"],
        "answered": set(),
        "created": time.time(),
    }
    title = "🧠 تست هوش سکتور" if kind == "intel" else "🧩 معمای منطقی سکتور"
    await update.effective_message.reply_text(
        f"{title}\n\n{item['q']}\n\n👇 یکی از گزینه‌ها رو انتخاب کن:\n🎁 جایزه پاسخ درست: ۵ سکه + ۱۰ XP",
        reply_markup=_quiz_keyboard(qid, item["options"]),
    )


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return
    parts = query.data.split(":")
    if len(parts) != 3:
        await query.answer("درخواست نامعتبره.")
        return
    _, qid, raw_choice = parts
    state = quiz_states.get(qid)
    if not state or time.time() - state["created"] > 3600:
        await query.answer("⏳ این سؤال منقضی شده؛ یک سؤال جدید بگیر.", show_alert=True)
        return
    user_id = query.from_user.id
    if user_id in state["answered"]:
        await query.answer("قبلاً به این سؤال جواب دادی 🙂", show_alert=True)
        return
    try:
        choice = int(raw_choice)
    except ValueError:
        await query.answer("گزینه نامعتبره.")
        return
    if choice < 0 or choice >= len(state["options"]):
        await query.answer("گزینه نامعتبره.")
        return
    state["answered"].add(user_id)
    if choice == state["correct"]:
        coins, xp, level = _award_quiz(query.from_user, 5, 10)
        await query.answer(f"✅ درست بود! +۵ سکه 🪙  +۱۰ XP ⭐\nسطح: {level}", show_alert=True)
    else:
        correct = state["options"][state["correct"]]
        await query.answer(f"❌ اشتباه بود.\n✅ پاسخ درست: {correct}\n💡 {state['explain']}", show_alert=True)


async def games_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.utils.keyboards import get_games_menu
    await update.effective_message.reply_text("🎮 منوی بازی‌های سکتور:", reply_markup=get_games_menu())
    raise ApplicationHandlerStop()


async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_dice(emoji="🎲")
    raise ApplicationHandlerStop()


async def coin_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_dice(emoji="🪙")
    raise ApplicationHandlerStop()


async def start_number_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    target = random.randint(1, 100)
    _save_game(chat_id, {"type": "number_guess", "target": target, "attempts": 0, "max_attempts": 7, "user_id": update.effective_user.id})
    await update.effective_message.reply_text("🎯 بازی حدس عدد شروع شد!\nمن یک عدد بین ۱ تا ۱۰۰ انتخاب کردم. ۷ فرصت داری.\n\nعدد مورد نظرت رو بفرست:")
    raise ApplicationHandlerStop()


async def handle_number_guess(update, context, state):
    text = update.effective_message.text
    if not text.isdigit():
        raise ApplicationHandlerStop()
    guess = int(text)
    state["attempts"] += 1
    chat_id = update.effective_chat.id
    if guess == state["target"]:
        await update.effective_message.reply_text(f"🎉 درست بود! عدد {guess} بود. ✅")
        _delete_game(chat_id)
    elif state["attempts"] >= state["max_attempts"]:
        await update.effective_message.reply_text(f"💀 فرصت‌ها تموم شد. عدد {state['target']} بود.")
        _delete_game(chat_id)
    elif guess < state["target"]:
        _save_game(chat_id, state)
        await update.effective_message.reply_text("📈 بزرگتر!")
    else:
        _save_game(chat_id, state)
        await update.effective_message.reply_text("📉 کوچکتر!")
    raise ApplicationHandlerStop()


async def start_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = ["سکتور", "تلگرام", "برنامه", "پایتون", "هوشمند", "سرگرمی", "فرمانده", "ایران", "تکنولوژی", "دیجیتال"]
    word = random.choice(words)
    scrambled = list(word)
    random.shuffle(scrambled)
    scrambled = "".join(scrambled)
    _save_game(update.effective_chat.id, {"type": "word_guess", "word": word, "user_id": update.effective_user.id})
    await update.effective_message.reply_text(f"📝 بازی حدس کلمه!\n\n`{scrambled}`\n\nکلمه درست چیه؟", parse_mode="Markdown")
    raise ApplicationHandlerStop()


async def handle_word_guess(update, context, state):
    if update.effective_message.text.strip() == state["word"]:
        await update.effective_message.reply_text(f"✅ آفرین! '{state['word']}' درست بود. 🏆")
        _delete_game(update.effective_chat.id)
    raise ApplicationHandlerStop()


async def start_flag_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recent = list(context.user_data.get("recent_flags", []))
    fresh = [item for item in _FLAGS if item[0] not in recent] or _FLAGS
    code, flag, country, _ = random.choice(fresh)
    context.user_data["recent_flags"] = (recent + [code])[-12:]
    _save_game(update.effective_chat.id, {"type": "flag_guess", "country": country, "user_id": update.effective_user.id})
    await update.effective_message.reply_text(f"🚩 این پرچم کدوم کشوره؟\n\n{flag}")
    raise ApplicationHandlerStop()


async def handle_flag_guess(update, context, state):
    if update.effective_message.text.strip() == state["country"]:
        await update.effective_message.reply_text(f"✅ درسته! {state['country']} 🌟")
        _delete_game(update.effective_chat.id)
    raise ApplicationHandlerStop()


async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text == "✂️ سنگ کاغذ قیچی":
        await update.effective_message.reply_text("✂️ یکی رو انتخاب کن: سنگ، کاغذ یا قیچی؟")
        raise ApplicationHandlerStop()
    user_choice = text.replace("✂️", "").strip()
    if user_choice not in ["سنگ", "کاغذ", "قیچی"]:
        return
    bot_choice = random.choice(["سنگ", "کاغذ", "قیچی"])
    if user_choice == bot_choice:
        result = "🤝 مساوی شدیم!"
    elif (user_choice, bot_choice) in [("سنگ", "قیچی"), ("کاغذ", "سنگ"), ("قیچی", "کاغذ")]:
        result = "🎉 تو برنده شدی!"
    else:
        result = "😜 من بردم!"
    await update.effective_message.reply_text(f"👤 تو: {user_choice}\n🤖 سکتور: {bot_choice}\n\n{result}")
    raise ApplicationHandlerStop()


async def start_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.effective_message.reply_text("⚔️ روی پیام رقیب ریپلای کن و بنویس: دوئل")
        raise ApplicationHandlerStop()
    p1, p2 = update.effective_user, update.message.reply_to_message.from_user
    if p1.id == p2.id:
        await update.effective_message.reply_text("❌ نمی‌تونی با خودت دوئل کنی!")
        raise ApplicationHandlerStop()
    winner = random.choice([p1, p2])
    await update.effective_message.reply_text(f"⚔️ دوئل!\n\n🏆 برنده: {winner.mention_html()}", parse_mode="HTML")
    raise ApplicationHandlerStop()


async def intelligence_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_quiz(update, context, "intel")
    raise ApplicationHandlerStop()


async def logic_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_quiz(update, context, "logic")
    raise ApplicationHandlerStop()


async def daily_lucky_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.date.today().isoformat()
    rng = random.Random(f"{user_id}-{today}")
    score = rng.randint(1, 100)
    res = "🌟 فوق‌العاده!" if score > 90 else "😊 خوبه." if score > 70 else "😐 معمولیه." if score > 40 else "😅 امروز زیاد روی شانس حساب نکن!"
    await update.effective_message.reply_text(f"🎲 میزان شانس امروز شما: {score}%\n\n{res}")
    raise ApplicationHandlerStop()


async def speed_contest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_to_type = random.choice(["سکتور بهترین ربات تلگرامه", "من عاشق بازی‌های سکتورلند هستم", "برنامه‌نویسی با پایتون خیلی خوبه"])
    await update.effective_message.reply_text(f"🏆 مسابقه سرعت پاسخ\n\nهرکی زودتر این جمله رو دقیق بفرسته برنده است:\n\n`{text_to_type}`", parse_mode="Markdown")
    _save_game(update.effective_chat.id, {"type": "speed_contest", "text": text_to_type, "start_time": time.time()})
    raise ApplicationHandlerStop()


async def game_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = _load_game(chat_id)
    if not state:
        return
    text = update.effective_message.text.strip()
    # Solo games belong to the user who started them. Other group members must
    # not consume attempts, solve, or cancel somebody else's round.
    owner_id = state.get("user_id")
    if owner_id and owner_id != update.effective_user.id:
        return
    if state["type"] == "number_guess":
        await handle_number_guess(update, context, state)
    elif state["type"] == "word_guess":
        await handle_word_guess(update, context, state)
    elif state["type"] == "flag_guess":
        await handle_flag_guess(update, context, state)
    elif state["type"] == "speed_contest" and text == state["text"]:
        elapsed = round(time.time() - state["start_time"], 2)
        await update.effective_message.reply_text(f"🎉 {update.effective_user.mention_html()} برنده شد!\n⏱ {elapsed} ثانیه", parse_mode="HTML")
        _delete_game(chat_id)
        raise ApplicationHandlerStop()
    elif text == "انصراف از بازی":
        _delete_game(chat_id)
        await update.effective_message.reply_text("❌ بازی متوقف شد.")
        raise ApplicationHandlerStop()
    raise ApplicationHandlerStop()


def get_handlers():
    return [
        CallbackQueryHandler(quiz_callback, pattern=r"^quiz:"),
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
        MessageHandler(filters.TEXT & ~filters.COMMAND, game_input_handler),
    ]
