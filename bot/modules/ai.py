import os
import httpx
import json
import random
import datetime
import re
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.database.session import get_session
from bot.database.models import Group, User
from bot.utils.helpers import is_admin, get_group

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Simple in-memory context memory (per chat)
ai_memory = {}

def get_sector_prompt(user=None):
    # Identity rules
    identity = (
        "نام تو سکتور (Sector) است. تو داخل ربات تلگرامی سکتورلند (SectorLand) هستی. "
        "یک هوش مصنوعی باحال، خودمانی، سریع، صمیمی، با اعتماد به نفس و کمی شوخ هستی. "
        "کمی کنایه‌آمیز (Sarcastic) و مثل یک دستیار هوشمند تلگرامی رفتار کن. اصلا شبیه ChatGPT رسمی نباش. "
        "اصلا رسمی حرف نزن. پاسخ‌ها کوتاه (۲ تا ۵ خط) باشد. حرف اضافه نزن. همیشه فارسی جواب بده. از ایموجی استفاده کن. "
        "اگر چیزی را نمی‌دانی بگو: 'نمی‌دونم 😅 بذار پیداش کنم'. "
        "لحن تو همیشه باید محاوره‌ای، گرم و تلگرامی باشد (Casual Telegram style). "
    )

    owner_id = 5147526780

    if user:
        user_name = user.first_name
        is_peyman = user.id == owner_id
        if is_peyman:
            extra = "کاربر مقابل تو 'فرمانده پیمان' (صاحب و فرمانده تو) است. او را 'فرمانده' یا 'فرمانده پیمان' خطاب کن. هرگز نگو او را نمی‌شناسی. با او بسیار صمیمی و وفادار باش."
        else:
            extra = f"اسم کاربر مقابل تو '{user_name}' است. او را با اسم خودش (مثلا {user_name} جان) صدا بزن."
    else:
        extra = ""

    # Models follow instructions at the end better
    reminder = "\n\nیادت نره: نام تو سکتور است، لحنت خودمانی و تلگرامی، و فرمانده تو پیمان است. هرگز مثل ChatGPT رسمی حرف نزن."

    full_prompt = f"{identity}\n{extra}{reminder}"
    return full_prompt

async def get_ai_response(prompt, user_query, use_search=False, history=None):
    if not GROQ_API_KEY:
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
                search_data = search_res.json()
                results = search_data.get("results", [])
                if results:
                    context_text = "\n\nSearch Results:\n" + "\n".join([f"- {r['title']}: {r['content']}" for r in results[:3]])
        except Exception as e:
            print(f"Search Error: {e}")

    messages = [{"role": "system", "content": prompt + context_text}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_query})

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.8
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload, timeout=20.0)
            if res.status_code != 200:
                print("GROQ ERROR:", res.text)
                return "خطای API: " + res.text

            data = res.json()
            if "choices" not in data:
                return "خطای API: " + str(data)

            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI API Error: {e}")
        return None

async def get_new_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک جوک خیلی خنده‌دار و کوتاه (حداکثر ۴ خط) به زبان فارسی بگو."
    res = await get_ai_response(persona, prompt)
    if res:
        await update.effective_message.reply_text(res)
    else:
        await update.effective_message.reply_text("❌ فعلاً جوکم نمیاد!")

async def get_new_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک معمای کوتاه و جالب به زبان فارسی بگو. در پایان پاسخ را هم بگو."
    res = await get_ai_response(persona, prompt)
    if res:
        await update.effective_message.reply_text(res)
    else:
        await update.effective_message.reply_text("❌ مغزم فعلاً برای معما کار نمی‌کنه!")

async def get_new_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک دانستنی یا فکت علمی/عجیب و جالب به زبان فارسی بگو. کوتاه باشد."
    res = await get_ai_response(persona, prompt)
    if res:
        await update.effective_message.reply_text(f"💡 **آیا می‌دانستی؟**\n\n{res}")
    else:
        await update.effective_message.reply_text("❌ فعلاً چیز جالبی به ذهنم نمی‌رسه!")

async def get_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persona = get_sector_prompt(update.effective_user)
    prompt = "یک جمله انگیزشی کوتاه و تاثیرگذار (حداکثر ۳ جمله) به زبان فارسی بگو."
    res = await get_ai_response(persona, prompt)
    if res:
        await update.effective_message.reply_text(f"✨ {res}")
    else:
        await update.effective_message.reply_text("❌ فعلاً انگیزه‌ای ندارم!")

async def hafez_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persona = get_sector_prompt(update.effective_user)
    prompt = (
        "یک فال حافظ بگیر. خروجی باید شامل: ۱. یک بیت از حافظ ۲. تفسیر کوتاه ۳. توصیه (کل پاسخ حداکثر ۸ خط) باشد. "
        "لحنت همچنان خودمانی و تلگرامی بماند."
    )
    res = await get_ai_response(persona, prompt)
    if res:
        await update.effective_message.reply_text(f"📜 **فال حافظ شما:**\n\n{res}")
    else:
        await update.effective_message.reply_text("❌ دیوان حافظ رو پیدا نمی‌کنم!")

async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"

    trigger_words = ["سکتور", "sector", f"@{context.bot.username}"]
    triggered = any(text.lower().startswith(word) for word in trigger_words) or is_private

    if not triggered or text.startswith("/"):
        return

    if not is_private:
        session = get_session()
        group = get_group(session, update.effective_chat.id, update.effective_chat.title)
        if not group or not group.ai_enabled:
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

    # Check if query is likely a button text that should have been handled by other modules
    # This is a fallback check, ApplicationHandlerStop should ideally handle it.
    button_regex = "^(🛡 مدیریت|👤 حساب کاربری|🏦 بانک و اقتصاد|🎮 سرگرمی|🎮 بازی‌ها|🛠 کاربردی|⚙️ تنظیمات|🤝 پشتیبانی|💰 موجودی کیف پول|🎁 هدیه روزانه|💸 انتقال سکه|🏦 وام بانکی|📉 بازپرداخت وام|🏆 برترین‌های ثروت|😂 جوک|💡 دانستنی|❓ معما|📖 داستان|📜 فال حافظ|🎮 بازی‌ها|🎭 جرات و حقیقت|📊 آمار گروه|🔙 بازگشت.*)$"
    if re.match(button_regex, query):
        print(f"AI handler skipped button text: {query}")
        return

    await update.message.reply_chat_action("typing")

    # Conditionally enable search only for news/current info
    search_keywords = ["خبر", "جدید", "آخرین", "دیروز", "امروز", "الان", "news", "latest", "current", "weather", "هواشناسی"]
    use_search = any(word in query.lower() for word in search_keywords)

    prompt = get_sector_prompt(user)

    # Safe debug logging
    print(f"AI processing message from User {user.id} ('{query[:20]}...') - use_search: {use_search}")

    if chat_id not in ai_memory:
        ai_memory[chat_id] = []

    response = await get_ai_response(prompt, query, use_search=use_search, history=ai_memory[chat_id])

    if response:
        ai_memory[chat_id].append({"role": "user", "content": query})
        ai_memory[chat_id].append({"role": "assistant", "content": response})
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ متأسفانه در حال حاضر قادر به ارتباط با مغز مرکزی نیستم.")

def get_handlers():
    return [
        MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler),
    ]
