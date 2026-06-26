import os
import httpx
import json
import random
import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import Group, User
from bot.utils.helpers import is_admin

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Simple in-memory context memory (per user/chat)
ai_memory = {} # {chat_id: [{"role": "user", "content": "..."}, ...]}

async def get_ai_response(prompt, user_query, use_search=False, history=None):
    context_text = ""
    if use_search and TAVILY_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                search_res = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": TAVILY_API_KEY, "query": user_query, "search_depth": "basic"}
                )
                search_data = search_res.json()
                results = search_data.get("results", [])
                if results:
                    context_text = "\n\nSearch Results:\n" + "\n".join([f"- {r['title']}: {r['content']}" for r in results[:3]])
        except Exception as e:
            print(f"Search Error: {e}")

    messages = [{"role": "system", "content": prompt + context_text}]
    if history:
        messages.extend(history[-6:]) # Keep last 6 exchanges
    messages.append({"role": "user", "content": user_query})

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama3-70b-8192",
            "messages": messages
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload, timeout=30.0)
            data = res.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI API Error: {e}")
        return None

async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"

    # Check triggers
    trigger_words = ["سکتور", "sector", f"@{context.bot.username}"]
    triggered = any(text.lower().startswith(word) for word in trigger_words) or is_private

    if not triggered or text.startswith("/"):
        return

    # If in group, check if enabled
    if not is_private:
        session = get_session()
        group = session.query(Group).filter(Group.id == update.effective_chat.id).first()
        if group and not group.ai_enabled:
            await update.message.reply_text("❌ دسترسی به هوش مصنوعی در این گروه توسط مدیران غیرفعال شده است.")
            session.close()
            return
        session.close()

    query = text
    for word in trigger_words:
        if query.lower().startswith(word):
            query = query[len(word):].strip()
            break

    if not query:
        return

    await update.message.reply_chat_action("typing")

    prompt = "You are SectorBot, a professional Persian AI assistant. Respond fluently in Persian (Farsi). Use emojis."

    if chat_id not in ai_memory:
        ai_memory[chat_id] = []

    response = await get_ai_response(prompt, query, use_search=True, history=ai_memory[chat_id])

    if response:
        ai_memory[chat_id].append({"role": "user", "content": query})
        ai_memory[chat_id].append({"role": "assistant", "content": response})
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ متأسفانه در حال حاضر قادر به پاسخگویی نیستم.")

async def get_new_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    res = await get_ai_response("یک جوک جدید و خنده‌دار متفاوت به زبان فارسی بگو. تکراری نباشد.", "جوک بگو")
    await update.message.reply_text(res or "😂 فعلاً حوصله خندیدن ندارم!")

async def get_new_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    res = await get_ai_response("یک معما جدید به همراه پاسخ (با کمی فاصله) به زبان فارسی بگو.", "معما بگو")
    await update.message.reply_text(res or "❓ معما چو حل گشت آسان شود!")

async def get_new_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    res = await get_ai_response("یک دانستنی علمی یا جالب جدید و عجیب به زبان فارسی بگو.", "دانستنی بگو")
    await update.message.reply_text(res or "💡 دانستن توانستن است!")

async def get_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    res = await get_ai_response("یک متن انگیزشی کوتاه و انرژی‌بخش جدید به زبان فارسی بگو.", "متن انگیزشی")
    await update.message.reply_text(res or "✨ تو می‌تونی!")

async def hafez_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    prompt = (
        "Generate a Hafez fortune in Persian. Include: "
        "1. A random verse from Hafez. "
        "2. An interpretation (تعبیر). "
        "3. The deeper meaning (مفهوم). "
        "4. A final result (نتیجه فال). "
        "Make it poetic and beautiful with emojis."
    )
    res = await get_ai_response(prompt, "فال حافظ بگیر")
    await update.message.reply_text(res or "📜 حافظ گشودیم و فال نیامد...")

def get_handlers():
    return [
        MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler),
    ]
