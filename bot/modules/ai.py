import os
import httpx
import json
import random
import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import Group, User
from bot.utils.helpers import is_admin, get_group, get_reply_text

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Simple in-memory context memory (per chat)
ai_memory = {}

async def get_ai_response(prompt, user_query, use_search=False, history=None):
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found in environment.")
        return None

    context_text = ""
    if use_search and TAVILY_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                search_res = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": TAVILY_API_KEY, "query": user_query, "search_depth": "basic"},
                    timeout=10.0
                )
                if search_res.status_code == 200:
                    search_data = search_res.json()
                    results = search_data.get("results", [])
                    if results:
                        context_text = "\n\nRelevant Information from Search:\n" + "\n".join([f"- {r['title']}: {r['content']}" for r in results[:3]])
        except Exception as e:
            print(f"Search API Error: {e}")

    # Build message payload
    messages = [{"role": "system", "content": prompt + context_text}]
    if history:
        messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_query})

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload, timeout=30.0)

            if res.status_code != 200:
                print(f"Groq API Error: {res.status_code}")
                try:
                    error_json = res.json()
                    print(f"Detailed Groq Error: {json.dumps(error_json, indent=2)}")
                except:
                    print(f"Raw Error Body: {res.text}")
                return None

            data = res.json()
            # Enhanced robustness for non-standard responses
            if "choices" in data and len(data["choices"]) > 0 and "message" in data["choices"][0]:
                return data["choices"][0]["message"]["content"].strip()
            else:
                print(f"Groq API Unexpected Response Structure: {data}")
                return None

    except Exception as e:
        print(f"AI api_call Exception: {e}")
        return None

async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"

    # AI Triggers
    trigger_words = ["سکتور", "sector", f"@{context.bot.username}"]
    triggered = any(text.lower().startswith(word) for word in trigger_words) or is_private

    # Ignore commands or non-triggered group messages
    if not triggered or text.startswith("/"):
        return

    # Group enable check
    if not is_private:
        session = get_session()
        group = get_group(session, update.effective_chat.id, update.effective_chat.title)
        if not group or not group.ai_enabled:
            # Silent ignore if not found or disabled
            session.close()
            return
        session.close()

    query = text
    for word in trigger_words:
        if query.lower().startswith(word):
            query = query[len(word):].strip()
            break

    if not query or len(query) < 2: return

    await update.effective_message.reply_chat_action("typing")

    prompt = "You are SectorBot, a helpful and professional Persian AI assistant. Speak like a friendly human in Persian. Use emojis."

    if chat_id not in ai_memory:
        ai_memory[chat_id] = []

    history = ai_memory[chat_id] if is_private else None

    response = await get_ai_response(prompt, query, use_search=True, history=history)

    if response:
        if is_private:
            ai_memory[chat_id].append({"role": "user", "content": query})
            ai_memory[chat_id].append({"role": "assistant", "content": response})
            if len(ai_memory[chat_id]) > 10:
                ai_memory[chat_id] = ai_memory[chat_id][-10:]

        reply_txt = await get_reply_text(update.effective_user, response)
        # Final safety against Markdown errors
        try:
            await update.effective_message.reply_text(reply_txt, parse_mode=None)
        except Exception as e:
            print(f"Telegram Send Error: {e}")
            await update.effective_message.reply_text(reply_txt.replace("*", "").replace("_", "").replace("`", ""), parse_mode=None)
    else:
        await update.effective_message.reply_text("❌ متأسفانه قادر به ارتباط با مغز مرکزی نیستم.")

async def get_new_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    res = await get_ai_response("یک جوک جدید و خنده‌دار متفاوت به زبان فارسی بگو. تکراری نباشد.", "جوک بگو")
    fallback = "‏غواصه میره زیر آب، میبینه یه ماهی داره غرق میشه! نجاتش میده! 😂"
    await update.effective_message.reply_text(res or fallback, parse_mode=None)

async def get_new_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    res = await get_ai_response("یک معما جدید به همراه پاسخ به زبان فارسی بگو.", "معما بگو")
    fallback = "❓ آن چیست که پا دارد اما راه نمی‌رود؟\n\n✅ پاسخ: میز 🪑"
    await update.effective_message.reply_text(res or fallback, parse_mode=None)

async def get_new_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    res = await get_ai_response("یک دانستنی علمی یا جالب جدید و عجیب به زبان فارسی بگو.", "دانستنی بگو")
    fallback = "💡 آیا می‌دانستید که هشت‌پاها سه قلب دارند؟ 🐙"
    await update.effective_message.reply_text(res or fallback, parse_mode=None)

async def get_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    res = await get_ai_response("یک متن انگیزشی کوتاه و انرژی‌بخش جدید به زبان فارسی بگو.", "متن انگیزشی")
    fallback = "✨ هرگز تسلیم نشو، معجزه‌ها هر روز رخ می‌دهند."
    await update.effective_message.reply_text(res or fallback, parse_mode=None)

async def hafez_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_chat_action("typing")
    prompt = (
        "Generate a Hafez fortune in Persian. Include: "
        "1. A random verse from Hafez. "
        "2. An interpretation (تعبیر). "
        "3. The deeper meaning (مفهوم). "
        "4. A final result (نتیجه فال). "
        "Make it poetic and beautiful with emojis."
    )
    res = await get_ai_response(prompt, "فال حافظ بگیر")
    fallback = (
        "📜 فال حافظ شما:\n\n"
        "📖 شعر:\nالا یا ایها الساقی ادر کأسا و ناولها\n\n"
        "💡 تعبیر:\nصبور باشید و به خداوند توکل کنید.\n\n"
        "🎯 نتیجه:\nموفقیت در انتظار شماست."
    )
    await update.effective_message.reply_text(res or fallback, parse_mode=None)

def get_handlers():
    return [
        MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler),
    ]
