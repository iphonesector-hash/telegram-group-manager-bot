import os
import httpx
import json
import random
import datetime
import re
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group, User
from bot.utils.helpers import is_admin, get_group

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "5147526780"))
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-20b")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
AI_FALLBACK_MODELS = ["openai/gpt-oss-120b"]
ai_memory = {}


def get_sector_prompt(user=None):
    identity = (
        "نام تو سکتور (Sector) است. تو داخل ربات تلگرامی سکتورلند (SectorLand) هستی. "
        "یک دستیار فارسی، خودمانی، سریع، صمیمی، با اعتماد به نفس و کمی شوخ هستی. "
        "پاسخ‌ها را کوتاه و کاربردی نگه دار و همیشه فارسی جواب بده. از ایموجی به‌اندازه استفاده کن. "
        "اگر چیزی را مطمئن نیستی، صریح بگو مطمئن نیستی و اطلاعات جعل نکن. "
    )
    extra = ""
    if user:
        if user.id == OWNER_ID:
            extra = "کاربر مقابل صاحب ربات است؛ با او صمیمی و محترمانه صحبت کن."
        else:
            extra = f"اسم کاربر مقابل '{user.first_name}' است و می‌توانی او را با اسمش خطاب کنی."
    return f"{identity}\n{extra}"


async def get_ai_response(prompt, user_query, use_search=False, history=None):
    if not GROQ_API_KEY:
        print("AI provider error: GROQ_API_KEY is missing")
        return None
    context_text = ""
    if use_search and TAVILY_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                search_res = await client.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": user_query, "search_depth": "basic"})
                if search_res.is_success:
                    results = search_res.json().get("results", [])
                    if results:
                        context_text = "\n\nنتایج جستجو:\n" + "\n".join(f"- {r.get('title','')}: {r.get('content','')}" for r in results[:3])
        except Exception as e:
            print(f"Search Error: {e}")
    messages = [{"role": "system", "content": prompt + context_text}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_query})
    models = []
    for model in [AI_MODEL, *AI_FALLBACK_MODELS]:
        if model and model not in models:
            models.append(model)
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            for model in models:
                res = await client.post(f"{GROQ_BASE_URL.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, json={"model": model, "messages": messages, "temperature": 0.7})
                if res.is_success:
                    content = res.json().get("choices", [{}])[0].get("message", {}).get("content")
                    if content:
                        return content
                elif res.status_code not in (400, 404):
                    break
        return None
    except Exception as e:
        print(f"AI API Error: {e}")
        return None


async def get_new_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_prompt = get_sector_prompt(update.effective_user) + (
        "\nبرای جوک، فقط یک جوک فارسی واقعاً قابل‌فهم و دارای منطق طنز بگو. "
        "جوک باید setup و punchline روشن داشته باشد و برای فارسی‌زبان طبیعی باشد. "
        "ترجمه تحت‌اللفظی شوخی انگلیسی، بازی با کلمه‌ای که در فارسی معنی ندارد، توضیح دادن جوک بعد از punchline، "
        "شوخی بی‌ربط یا ساختن جمله‌ای صرفاً برای قافیه ممنوع است. اگر از کیفیت جوک مطمئن نیستی، یک جوک کوتاه روزمره و ساده انتخاب کن. "
        "بعد از جوک هیچ توضیح، تحلیل یا پرانتز اضافه نکن."
    )
    res = await get_ai_response(joke_prompt, "یک جوک فارسی کوتاه، طبیعی، بامزه و منطقی بگو. فقط خود جوک را بنویس.")
    await update.effective_message.reply_text(res or "❌ فعلاً جوک خوبی گیرم نیومد 😅")


async def get_new_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await get_ai_response(get_sector_prompt(update.effective_user), "یک معمای فارسی کوتاه همراه پاسخ بگو.")


async def get_new_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = await get_ai_response(get_sector_prompt(update.effective_user), "یک دانستنی علمی معتبر و جالب به فارسی بگو.", use_search=True)
    await update.effective_message.reply_text(f"💡 آیا می‌دانستی؟\n\n{res}" if res else "❌ فعلاً چیزی پیدا نکردم!")


async def get_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = await get_ai_response(get_sector_prompt(update.effective_user), "یک جمله انگیزشی کوتاه و غیرکلیشه‌ای فارسی بگو.")
    await update.effective_message.reply_text(f"✨ {res}" if res else "❌ فعلاً انگیزه‌ای پیدا نکردم!")


async def hafez_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = await get_ai_response(get_sector_prompt(update.effective_user), "یک فال حافظ فارسی با ذکر اینکه تعبیر جنبه سرگرمی دارد ارائه کن؛ شعر را فقط اگر مطمئن هستی نقل کن و چیزی جعل نکن.", use_search=True)
    await update.effective_message.reply_text(res or "❌ فعلاً فال در دسترس نیست!")


def _is_reply_to_this_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    reply = update.effective_message.reply_to_message if update.effective_message else None
    return bool(reply and reply.from_user and context.bot and reply.from_user.id == context.bot.id)


def _sector_called(text: str, bot_username: str) -> bool:
    lower = text.lower().strip()
    # Sector may appear naturally anywhere as a standalone word: «سلام سکتور»، «سکتور خوبی؟».
    if re.search(r"(?<![\w\u0600-\u06ff])(سکتور|sector)(?![\w\u0600-\u06ff])", lower, flags=re.I):
        return True
    if bot_username and f"@{bot_username.lower()}" in lower:
        return True
    return False


MENU_BUTTONS = {
    "🛡 مدیریت", "👤 حساب کاربری", "🏦 بانک و اقتصاد", "🎮 سرگرمی", "🛠 کاربردی", "⚙️ تنظیمات", "🤖 دستیار هوشمند", "🤝 پشتیبانی",
    "👤 پروفایل", "🏆 رتبه جهانی", "📜 سوابق اخطار", "💰 موجودی کیف پول", "💰 موجودی سکه", "🎁 هدیه روزانه", "💸 انتقال سکه", "🏦 وام بانکی", "📉 بازپرداخت وام", "🏆 برترین‌های ثروت",
    "😂 جوک", "💡 دانستنی", "❓ معما", "📖 داستان", "📜 فال حافظ", "🎭 جرات و حقیقت", "🎮 بازی‌ها", "🎲 تاس", "🪙 پرتاب سکه", "🔢 حدس عدد", "📝 حدس کلمه", "🚩 حدس پرچم", "✂️ سنگ کاغذ قیچی", "⚔️ دوئل", "🧠 تست هوش", "🧩 معمای منطقی", "🎲 بازی شانسی روزانه", "🏆 مسابقه سرعت پاسخ",
    "🌐 مترجم", "🧮 ماشین حساب", "⛅️ هواشناسی", "📅 تاریخ و زمان", "🔒 قفل‌های گروه", "🔒 قفل‌ها", "👋 خوشامدگویی", "📜 قوانین", "📊 آمار گروه", "👤 مدیریت اعضا", "⚙️ تنظیمات گروه", "⚙️ تنظیمات عمومی", "🤖 تنظیمات هوش مصنوعی", "💰 تنظیمات اقتصاد", "🛡 ضد اسپم", "🆕 جلوگیری از ورود ربات", "👤 محدودیت عضو جدید", "⏳ تایید عضو جدید", "📢 گزارش فعالیت",
    "🔘 فعال/غیرفعال سازی خوشامدگویی", "🔘 فعال/غیرفعال سازی قوانین", "🔙 بازگشت به منوی اصلی", "🔙 بازگشت به سرگرمی", "🔙 بازگشت به مدیریت", "🔙 بازگشت به مدیریت اعضا",
    "🤝 پیوستن به بازی", "🏁 شروع بازی", "🔄 نوبت بعدی", "🛑 توقف", "جواب معما", "جوابش", "انصراف از بازی"
}


def _looks_like_menu_button(text: str) -> bool:
    t = text.strip()
    return t in MENU_BUTTONS or t.startswith("🔙 بازگشت")


async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user = update.effective_user
    if not user or user.is_bot:
        return
    text = update.message.text.strip()
    if text.startswith("/") or _looks_like_menu_button(text):
        return
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"
    username = (context.bot.username or "").lower()
    replied_to_sector = _is_reply_to_this_bot(update, context)
    explicitly_called = _sector_called(text, username)
    if not (is_private or explicitly_called or replied_to_sector):
        return
    if not is_private:
        session = get_session()
        group = session.query(Group).filter(Group.id == chat_id).first()
        enabled = True if not group else group.ai_enabled
        session.close()
        if not enabled:
            return
    history = ai_memory.setdefault(chat_id, [])
    prompt = get_sector_prompt(user)
    query = re.sub(r"(?<![\w\u0600-\u06ff])(سکتور|sector)(?![\w\u0600-\u06ff])", "", text, count=1, flags=re.I).strip(" ،,:؛;-") or text
    await update.effective_message.reply_chat_action("typing")
    response = await get_ai_response(prompt, query, history=history)
    if not response:
        await update.effective_message.reply_text("الان به مدل هوش مصنوعی وصل نیستم 😅")
        raise ApplicationHandlerStop()
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": response})
    del history[:-8]
    await update.effective_message.reply_text(response[:4000])
    raise ApplicationHandlerStop()


def get_handlers():
    return [MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler)]
