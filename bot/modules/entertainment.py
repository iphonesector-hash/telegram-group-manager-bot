import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.modules.ai import get_ai_response, get_sector_prompt, get_new_joke, get_new_riddle, get_new_fact, get_motivation, hafez_fortune
from bot.utils.keyboards import get_tod_menu, get_joke_categories_menu

# Multiplayer state for Truth or Dare
tod_sessions = {} # {chat_id: {"players": [id1, id2], "turn": 0, "active": False}}

async def story_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک داستان کوتاه، خلاقانه و جدید به زبان فارسی بنویس. از اینترنت برای الهام گرفتن از سوژه‌های روز استفاده کن."
    res = await get_ai_response(persona, prompt, use_search=True)
    await update.effective_message.reply_text(res or "📖 کتاب قصه‌هام فعلاً باز نمیشه!")
    raise ApplicationHandlerStop()

async def riddle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    res = await get_new_riddle(update, context)
    if res and "|" in res:
        parts = res.split("|")
        riddle = parts[0].replace("معما:", "").strip()
        answer = parts[1].replace("پاسخ:", "").strip()
        context.chat_data["riddle_answer"] = answer
        await update.effective_message.reply_text(f"❓ **معمای جدید:**\n\n{riddle}\n\n💡 برای دیدن جواب بنویسید: جواب معما")
    else:
        await update.effective_message.reply_text("❌ مشکلی در طرح معما پیش اومد.")
    raise ApplicationHandlerStop()

async def reveal_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = context.chat_data.get("riddle_answer")
    if answer:
        await update.effective_message.reply_text(f"✅ پاسخ معما:\n\n{answer}")
        del context.chat_data["riddle_answer"]
    else:
        await update.effective_message.reply_text("❌ هنوز معمایی طرح نشده!")
    raise ApplicationHandlerStop()

async def joke_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    if text == "😂 جوک":
        await update.effective_message.reply_text("🤣 دسته جوک رو انتخاب کن:", reply_markup=get_joke_categories_menu())
    else:
        await get_new_joke(update, context)
    raise ApplicationHandlerStop()

# --- Multiplayer Truth or Dare ---
async def start_tod_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id in tod_sessions and tod_sessions[chat_id]["active"]:
        await update.effective_message.reply_text("⚠️ یک بازی در جریان است. بنویسید 'توقف بازی' برای لغو.")
        raise ApplicationHandlerStop()

    tod_sessions[chat_id] = {
        "players": [{"id": user.id, "name": user.first_name}],
        "turn": 0,
        "active": False
    }

    await update.effective_message.reply_text(
        f"🎭 **بازی جرات و حقیقت سکتور**\n\n"
        f"👤 شروع کننده: {user.first_name}\n\n"
        f"بقیه هم برای شرکت در بازی روی دکمه '🤝 پیوستن به بازی' کلیک کنن یا بنویسن: 'منم هستم'",
        reply_markup=get_tod_menu()
    )
    raise ApplicationHandlerStop()

async def join_tod_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in tod_sessions:
        return

    session = tod_sessions[chat_id]
    if any(p["id"] == user.id for p in session["players"]):
        await update.effective_message.reply_text(f"✅ {user.first_name}، شما قبلاً وارد بازی شدی!")
        raise ApplicationHandlerStop()

    session["players"].append({"id": user.id, "name": user.first_name})
    await update.effective_message.reply_text(f"🤝 {user.first_name} به بازی اضافه شد! (تعداد بازیکنان: {len(session['players'])})")
    raise ApplicationHandlerStop()

async def begin_tod_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in tod_sessions: return

    session = tod_sessions[chat_id]
    if len(session["players"]) < 2:
        await update.effective_message.reply_text("❌ برای شروع حداقل به ۲ نفر نیاز داریم!")
        raise ApplicationHandlerStop()

    session["active"] = True
    await update.effective_message.reply_text("🏁 بازی شروع شد! نوبت‌ها مشخص میشه...")
    await asyncio.sleep(1)
    await next_tod_turn(update, context)
    raise ApplicationHandlerStop()

async def next_tod_turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in tod_sessions: return
    session = tod_sessions[chat_id]

    p_from = session["players"][session["turn"]]
    session["turn"] = (session["turn"] + 1) % len(session["players"])
    p_to = session["players"][session["turn"]]

    await update.effective_message.reply_text(
        f"🔄 نوبت بازی:\n\n"
        f"🗣 **{p_from['name']}** باید از **{p_to['name']}** بپرسه:\n"
        f"**جرات یا حقیقت؟**",
        reply_markup=get_tod_menu()
    )
    raise ApplicationHandlerStop()

async def tod_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    chat_id = update.effective_chat.id

    if chat_id not in tod_sessions or not tod_sessions[chat_id]["active"]:
        if text in ["🎯 جرات", "💬 حقیقت", "🎲 تصادفی"]:
            # Single player mode fallback
            await update.effective_message.reply_chat_action("typing")
            mode = "جرات" if text == "🎯 جرات" else "حقیقت" if text == "💬 حقیقت" else random.choice(["جرات", "حقیقت"])
            prompt = f"یک چالش '{mode}' باحال، جدید و سرگرم‌کننده بگو. از اینترنت برای پیدا کردن چالش‌های تازه کمک بگیر."
            res = await get_ai_response(get_sector_prompt(update.effective_user), prompt, use_search=True)
            await update.effective_message.reply_text(f"🎭 {text}:\n\n{res}")
            raise ApplicationHandlerStop()
        return

    # Multiplayer logic
    await update.effective_message.reply_chat_action("typing")
    mode = "جرات" if text == "🎯 جرات" else "حقیقت" if text == "💬 حقیقت" else random.choice(["جرات", "حقیقت"])
    prompt = f"یک چالش '{mode}' جذاب و تازه برای بازی جرات و حقیقت بگو. پاسخ فقط شامل چالش باشد."
    res = await get_ai_response(get_sector_prompt(update.effective_user), prompt, use_search=True)

    await update.effective_message.reply_text(f"🎭 **{mode}:**\n\n{res}\n\nبعد از انجام چالش، '🔄 نوبت بعدی' رو بزنید یا بفرستید.")
    raise ApplicationHandlerStop()

async def stop_tod_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in tod_sessions:
        del tod_sessions[chat_id]
        await update.effective_message.reply_text("🛑 بازی متوقف شد.")
    raise ApplicationHandlerStop()

async def ent_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text

    if text == "💡 دانستنی":
        await get_new_fact(update, context)
    elif text == "📜 فال حافظ":
        await hafez_fortune(update, context)
    elif text == "❓ معما":
        await riddle_handler(update, context)
    elif text == "📖 داستان":
        await story_handler(update, context)
    elif text == "😂 جوک":
        await joke_handler(update, context)
    elif text in ["😂 خنده‌دار", "😈 شیطنتی", "🧠 هوشمندانه", "🤣 کوتاه"]:
        await get_new_joke(update, context)
    elif text == "🎯 چالش":
        await get_motivation(update, context)
    elif text == "🎮 بازی‌ها":
        from bot.utils.keyboards import get_games_menu
        await update.effective_message.reply_text("🎮 به بخش بازی‌های سکتور خوش اومدی!\nیکی رو انتخاب کن و شروع کنیم:", reply_markup=get_games_menu())
    else:
        return
    raise ApplicationHandlerStop()

def get_handlers():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^🎭 جرات و حقیقت$"), start_tod_session),
        MessageHandler(filters.TEXT & filters.Regex("^(منم هستم|🤝 پیوستن به بازی)$"), join_tod_session),
        MessageHandler(filters.TEXT & filters.Regex("^🏁 شروع بازی$"), begin_tod_play),
        MessageHandler(filters.TEXT & filters.Regex("^(بعدی|🔄 نوبت بعدی)$"), next_tod_turn),
        MessageHandler(filters.TEXT & filters.Regex("^(توقف بازی|🛑 توقف)$"), stop_tod_session),
        MessageHandler(filters.TEXT & filters.Regex("^(🎯 جرات|💬 حقیقت|🎲 تصادفی)$"), tod_action_handler),
        MessageHandler(filters.TEXT & filters.Regex("^جواب معما$"), reveal_riddle),
        MessageHandler(filters.TEXT & filters.Regex("^(😂 جوک|💡 دانستنی|❓ معما|📖 داستان|📜 فال حافظ|🎯 چالش|😂 خنده‌دار|😈 شیطنتی|🧠 هوشمندانه|🤣 کوتاه|🎮 بازی‌ها)$"), ent_button_handler),
    ]
