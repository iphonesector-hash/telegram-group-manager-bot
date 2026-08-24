import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_ai_response, get_sector_prompt, get_new_joke as get_ai_joke, get_new_riddle as get_ai_riddle, get_new_fact, get_motivation, hafez_fortune
from bot.utils.keyboards import get_games_menu, get_tod_menu, get_joke_categories_menu, get_entertainment_menu
from bot.services.runtime_state import delete_state, get_state, set_state

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
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک داستان کوتاه خلاقانه و جدید به زبان فارسی بنویس. داستان باید حداقل سه پاراگراف باشد و موضوعی جذاب داشته باشد. موضوع می‌تواند علمی-تخیلی یا فانتزی باشد."
    res = await get_ai_response(persona + "\n\n" + prompt, "یک داستان بگو")
    await update.effective_message.reply_text(res or "📖 متأسفانه کتاب داستانم فعلاً گم شده!", parse_mode=None)
    raise ApplicationHandlerStop()

async def get_riddle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    persona = get_sector_prompt(update.effective_user)
    recent = list(context.user_data.get("recent_riddles", []))
    avoid = "\n".join(f"- {item}" for item in recent[-8:])
    prompt = "یک معمای کوتاه، دقیق و تازه به زبان فارسی بگو. معمای تکراری یا بسیار معروف انتخاب نکن. فرمت خروجی دقیقا این باشد: معما: [متن] | پاسخ: [پاسخ]"
    if avoid:
        prompt += "\nمعما باید با موارد زیر متفاوت باشد:\n" + avoid
    res = await get_ai_response(persona + "\n\n" + prompt, "معما بگو")

    if res and "|" in res:
        parts = res.split("|")
        riddle = parts[0].replace("معما:", "").strip()
        answer = parts[1].replace("پاسخ:", "").strip()
        context.user_data["recent_riddles"] = (recent + [riddle])[-12:]
        riddle_answers[update.effective_chat.id] = answer
        set_state("riddle", str(update.effective_chat.id), {"answer": answer})
        await update.effective_message.reply_text(f"❓ {riddle}\n\n💡 برای دیدن جواب بنویسید: جواب معما یا جوابش؟", parse_mode=None)
    else:
        await get_ai_riddle(update, context)
    raise ApplicationHandlerStop()

async def reveal_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    durable = get_state("riddle", str(chat_id)) or {}
    answer = riddle_answers.get(chat_id) or durable.get("answer")
    if answer:
        await update.effective_message.reply_text(f"✅ پاسخ معما:\n\n{answer}", parse_mode=None)
        riddle_answers.pop(chat_id, None)
        delete_state("riddle", str(chat_id))
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
        # Since get_challenge_categories_menu is missing, we use a default message or simplified flow
        await get_tod_action(update, "dare")
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
    elif text == "🤝 پیوستن به بازی":
        saved=get_state("tod",str(update.effective_chat.id)) or {}
        players = context.chat_data.setdefault("tod_players", saved.get("players",[]))
        user = update.effective_user
        if not any(item["id"] == user.id for item in players):
            players.append({"id": user.id, "name": user.first_name})
            message = f"✅ {user.first_name} به بازی پیوست. تعداد بازیکنان: {len(players)}"
        else:
            message = "ℹ️ قبلاً به بازی پیوسته‌ای."
        set_state("tod",str(update.effective_chat.id),{"players":players,"turn":saved.get("turn",-1)})
        await update.effective_message.reply_text(message, reply_markup=get_tod_menu())
    elif text == "🏁 شروع بازی":
        saved=get_state("tod",str(update.effective_chat.id)) or {};players = context.chat_data.get("tod_players") or saved.get("players", [])
        if not players:
            await update.effective_message.reply_text("اول با دکمه «پیوستن به بازی» بازیکن‌ها را اضافه کنید.", reply_markup=get_tod_menu())
        else:
            context.chat_data["tod_turn"] = 0
            set_state("tod",str(update.effective_chat.id),{"players":players,"turn":0})
            await update.effective_message.reply_text(f"🏁 بازی شروع شد؛ نوبت {players[0]['name']} است.", reply_markup=get_tod_menu())
            await get_tod_action(update, "random")
    elif text == "🔄 نوبت بعدی":
        saved=get_state("tod",str(update.effective_chat.id)) or {};players = context.chat_data.get("tod_players") or saved.get("players", [])
        if not players:
            await update.effective_message.reply_text("بازی فعالی وجود ندارد.", reply_markup=get_tod_menu())
        else:
            turn = (int(context.chat_data.get("tod_turn", saved.get("turn",-1))) + 1) % len(players)
            context.chat_data["tod_turn"] = turn
            set_state("tod",str(update.effective_chat.id),{"players":players,"turn":turn})
            await update.effective_message.reply_text(f"🔄 نوبت {players[turn]['name']} است.", reply_markup=get_tod_menu())
            await get_tod_action(update, "random")
    elif text == "🛑 توقف":
        context.chat_data.pop("tod_players", None)
        context.chat_data.pop("tod_turn", None)
        delete_state("tod",str(update.effective_chat.id))
        await update.effective_message.reply_text("🛑 بازی متوقف شد.", reply_markup=get_entertainment_menu())
    elif text == "💡 دانستنی":
        await get_new_fact(update, context)
    elif text == "📜 فال حافظ":
        await hafez_fortune(update, context)
    elif text == "🎮 بازی‌ها":
        from bot.utils.keyboards import get_games_menu
        # Protective logging: print before sending, and catch any exception to log it.
        try:
            print("[TRACE] ent:ent_button_handler | sending games menu")
            await update.effective_message.reply_text(
                "🎮 به بخش بازی‌های سکتور خوش اومدی!\nیکی رو انتخاب کن و شروع کنیم:",
                reply_markup=get_games_menu()
            )
        except Exception as e:
            print(f"[ERROR] ent:ent_button_handler | exception while sending games menu: {e}", flush=True)
            raise
    elif text == "🔙 بازگشت به منوی اصلی":
        from bot.utils.keyboards import get_main_menu
        await update.effective_message.reply_text("🏠 بازگشت به منوی اصلی:", reply_markup=get_main_menu())
    elif text == "🔙 بازگشت به سرگرمی":
        from bot.utils.keyboards import get_entertainment_menu
        await update.effective_message.reply_text("🎮 بازگشت به منوی سرگرمی:", reply_markup=get_entertainment_menu())
    else:
        return

    raise ApplicationHandlerStop()

def get_handlers():
    return [
        CommandHandler("riddle", get_riddle_cmd),
        MessageHandler(filters.TEXT & filters.Regex("^(جواب معما|جوابش|جوابش؟)$"), reveal_riddle_answer),
        MessageHandler(filters.TEXT & filters.Regex("^(😂 جوک|💡 دانستنی|❓ معما|📖 داستان|🎯 چالش|📜 فال حافظ|🎮 بازی‌ها|🎭 جرات و حقیقت|😂 خنده‌دار|😈 شیطنتی|🧠 هوشمندانه|🤣 کوتاه|🎯 جرات|💬 حقیقت|🎲 تصادفی|🤝 پیوستن به بازی|🏁 شروع بازی|🔄 نوبت بعدی|🛑 توقف|🎯 چالش تصادفی|⚡ چالش سخت|😂 چالش خنده‌دار|🧠 چالش ذهنی|🔙 بازگشت به منوی اصلی|🔙 بازگشت به سرگرمی)$"), ent_button_handler),
    ]
