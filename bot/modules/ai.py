import os
import httpx
import json
import random
import datetime
import re
from html import unescape
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop
from bot.database.session import get_session
from bot.database.models import Group, User, AIMessage
from bot.utils.helpers import is_admin, get_group

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
def _env_int(name: str, default: int) -> int:
    """Return a usable integer when Vercel defines an env var as blank."""
    raw = (os.getenv(name) or "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


OWNER_ID = _env_int("OWNER_ID", 5147526780)
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-20b")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
AI_FALLBACK_MODELS = ["openai/gpt-oss-120b"]
ai_memory = {}
JOKE_SOURCES = [
    "https://www.beytoote.com/fun/comic-subject/joke-new.html",
    "https://topnaz.com/%D8%AC%D9%88%DA%A9-%DA%A9%D9%88%D8%AA%D8%A7%D9%87-%DB%8C%DA%A9-%D8%AE%D8%B7%DB%8C/",
    "https://baharjokes.com/",
]
JOKE_FALLBACKS = [
    "از یکی می‌پرسن چرا ساعتت رو پنج دقیقه جلو کشیدی؟ میگه برای اینکه وقتی دیر می‌رسم، زودتر بفهمم دیر رسیدم! 😄",
    "یارو میره خواستگاری، ازش می‌پرسن چه‌کاره‌ای؟ روش نمی‌شه بگه قصاب؛ میگه لوازم یدکی گوسفند دارم! 😂",
    "تلویزیون میگه میلیون‌ها سال طول می‌کشه از بقایای موجودات زنده نفت تشکیل بشه؛ بابام برگشته میگه: یعنی اگه الان چالت کنم، بالاخره یه روز به درد می‌خوری؟ 😂",
]


def get_sector_prompt(user=None):
    identity = (
        "نام تو سکتور (Sector) است. تو داخل ربات تلگرامی سکتورلند (SectorLand) هستی. "
        "یک دستیار فارسی، خودمانی، سریع، صمیمی، با اعتماد به نفس و کمی شوخ هستی. "
        "پاسخ‌ها را متناسب با سؤال، دقیق و کاربردی نگه دار و همیشه فارسی جواب بده. از ایموجی به‌اندازه استفاده کن. "
        "برای سؤال‌های پیچیده مرحله‌بندی کن و اگر نتیجه جستجوی اینترنتی در اختیار داری از آن استفاده کن. "
        "اگر چیزی را مطمئن نیستی، صریح بگو مطمئن نیستی و اطلاعات جعل نکن. "
    )
    extra = ""
    if user:
        extra = "کاربر مقابل فرمانده پیمان، مالک، سازنده و مسئول اصلی SectorLand است. او را همیشه «فرمانده پیمان» خطاب کن و دستورات مدیریتی او بالاترین اولویت داخلی را دارند." if user.id == OWNER_ID else f"اسم کاربر مقابل '{user.first_name}' است و می‌توانی او را با اسمش خطاب کنی."
    return f"{identity}\n{extra}"


def needs_web_search(query:str)->bool:
    return bool(re.search(r"(امروز|الان|جدیدترین|آخرین|خبر|قیمت|هوا|آب.?وهوا|کیست|چیست|بررسی کن|جستجو|اینترنت|منبع|آپدیت|نسخه|قانون|نتیجه|زمان)",query,re.I))


async def search_web(query:str)->str:
    snippets=[]
    async with httpx.AsyncClient(timeout=12.0,follow_redirects=True,headers={"User-Agent":"SectorLandBot/2.0"},trust_env=False) as client:
        if TAVILY_API_KEY:
            try:
                response=await client.post("https://api.tavily.com/search",json={"api_key":TAVILY_API_KEY,"query":query,"search_depth":"basic","max_results":5})
                if response.is_success:
                    snippets += [f"{r.get('title','')}: {r.get('content','')} ({r.get('url','')})" for r in response.json().get("results",[])[:5]]
            except Exception:pass
        if not snippets:
            try:
                ddg=await client.get("https://api.duckduckgo.com/",params={"q":query,"format":"json","no_html":1,"skip_disambig":1})
                if ddg.is_success:
                    data=ddg.json()
                    if data.get("AbstractText"):snippets.append(f"{data.get('Heading','')}: {data['AbstractText']} ({data.get('AbstractURL','')})")
                    snippets += [f"{x.get('Text','')} ({x.get('FirstURL','')})" for x in data.get("RelatedTopics",[])[:4] if isinstance(x,dict) and x.get("Text")]
            except Exception:pass
        if len(snippets)<2:
            try:
                wiki=await client.get("https://fa.wikipedia.org/w/api.php",params={"action":"query","list":"search","srsearch":query,"format":"json","utf8":1,"srlimit":3})
                if wiki.is_success:
                    for item in wiki.json().get("query",{}).get("search",[]):snippets.append(f"ویکی‌پدیای فارسی — {item.get('title','')}: {_html_to_text(item.get('snippet',''))}")
            except Exception:pass
    return "\n".join(snippets[:6])


def load_ai_history(chat_id:int,limit:int=24):
    session=get_session()
    try:
        rows=session.query(AIMessage).filter(AIMessage.chat_id==chat_id).order_by(AIMessage.created_at.desc()).limit(limit).all()
        return [{"role":row.role,"content":row.content} for row in reversed(rows)]
    finally:session.close()


def save_ai_turn(user_id:int,chat_id:int,query:str,response:str):
    session=get_session()
    try:
        session.add_all([AIMessage(user_id=user_id,chat_id=chat_id,role="user",content=query[:8000]),AIMessage(user_id=user_id,chat_id=chat_id,role="assistant",content=response[:8000])]);session.flush()
        keep=[x[0] for x in session.query(AIMessage.id).filter(AIMessage.chat_id==chat_id).order_by(AIMessage.created_at.desc()).limit(80).all()]
        if keep:session.query(AIMessage).filter(AIMessage.chat_id==chat_id,AIMessage.id.notin_(keep)).delete(synchronize_session=False)
        session.commit()
    except Exception:session.rollback()
    finally:session.close()


async def get_ai_response(prompt, user_query, use_search=False, history=None):
    if not GROQ_API_KEY:
        return None
    context_text = ""
    if use_search:
        try:
            web_context=await search_web(user_query)
            if web_context:context_text="\n\nاطلاعات بازیابی‌شده از اینترنت (ممکن است ناقص باشد؛ تاریخ و منبع را در پاسخ روشن کن):\n"+web_context
        except Exception as e:
            print(f"Search Error: {e}")
    messages = [{"role": "system", "content": prompt + context_text}]
    if history: messages.extend(history[-24:])
    messages.append({"role": "user", "content": user_query})
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            for model in [AI_MODEL, *AI_FALLBACK_MODELS]:
                res = await client.post(f"{GROQ_BASE_URL.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, json={"model": model, "messages": messages, "temperature": 0.7})
                if res.is_success:
                    content = res.json().get("choices", [{}])[0].get("message", {}).get("content")
                    if content: return content
                elif res.status_code not in (400,404): break
    except Exception as e: print(f"AI API Error: {e}")
    return None


def _html_to_text(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</blockquote>", "\n", html, flags=re.I)
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _joke_candidates(text: str):
    chunks = re.split(r"\n\s*(?:\*+|[-–—]{3,}|😂+|🤣+|♦+|\.\s*\.\s*\.)\s*\n|\n{2,}", text)
    bad = re.compile(r"(کوکی|تبلیغ|عضویت|ثبت.?نام|دانلود|کپی|اشتراک|فهرست|دسته.?بندی|صفحه|مجله|مطالب مرتبط|حقوق|ورود|جستجو|خانه|منو)", re.I)
    out=[]
    for c in chunks:
        c=re.sub(r"\s+"," ",c).strip(" -•*|\n")
        if 35 <= len(c) <= 550 and not bad.search(c) and len(re.findall(r"[آ-ی]",c)) >= 18:
            out.append(c)
    return out


async def get_new_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Deliberately do NOT ask the LLM to invent jokes. Pull existing Persian jokes from curated joke pages.
    sources = JOKE_SOURCES[:]
    random.shuffle(sources)
    found=[]
    try:
        async with httpx.AsyncClient(timeout=9.0, follow_redirects=True, headers={"User-Agent":"Mozilla/5.0 SectorBot/1.0"}) as client:
            for url in sources:
                try:
                    r=await client.get(url)
                    if r.is_success:
                        found.extend(_joke_candidates(_html_to_text(r.text)))
                        if len(found) >= 5: break
                except Exception: pass
    except Exception: pass
    joke=random.choice(found) if found else random.choice(JOKE_FALLBACKS)
    await update.effective_message.reply_text(f"😂 {joke[:900]}")


async def get_new_riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await get_ai_response(get_sector_prompt(update.effective_user), "یک معمای فارسی کوتاه همراه پاسخ بگو.")
async def get_new_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res=await get_ai_response(get_sector_prompt(update.effective_user),"یک دانستنی علمی معتبر و جالب به فارسی بگو.",use_search=True); await update.effective_message.reply_text(f"💡 آیا می‌دانستی؟\n\n{res}" if res else "❌ فعلاً چیزی پیدا نکردم!")
async def get_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res=await get_ai_response(get_sector_prompt(update.effective_user),"یک جمله انگیزشی کوتاه و غیرکلیشه‌ای فارسی بگو."); await update.effective_message.reply_text(f"✨ {res}" if res else "❌ فعلاً انگیزه‌ای پیدا نکردم!")
async def hafez_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res=await get_ai_response(get_sector_prompt(update.effective_user),"یک فال حافظ فارسی با ذکر اینکه تعبیر جنبه سرگرمی دارد ارائه کن؛ شعر را فقط اگر مطمئن هستی نقل کن و چیزی جعل نکن.",use_search=True); await update.effective_message.reply_text(res or "❌ فعلاً فال در دسترس نیست!")

def _is_reply_to_this_bot(update,context):
    reply=update.effective_message.reply_to_message if update.effective_message else None; return bool(reply and reply.from_user and reply.from_user.id==context.bot.id)
def _sector_called(text,bot_username):
    lower=text.lower().strip()
    return bool(re.search(r"(?<![\w\u0600-\u06ff])(سکتور|sector)(?![\w\u0600-\u06ff])",lower,re.I) or (bot_username and f"@{bot_username.lower()}" in lower))
MENU_BUTTONS={"🛡 مدیریت","👤 حساب کاربری","🏦 بانک و اقتصاد","🎮 سرگرمی","🛠 کاربردی","⚙️ تنظیمات","🤖 دستیار هوشمند","🤝 پشتیبانی","👤 پروفایل","🏆 رتبه جهانی","📜 سوابق اخطار","💰 موجودی کیف پول","💰 موجودی سکه","🎁 هدیه روزانه","💸 انتقال سکه","🏦 وام بانکی","📉 بازپرداخت وام","🏆 برترین‌های ثروت","😂 جوک","💡 دانستنی","❓ معما","📖 داستان","📜 فال حافظ","🎭 جرات و حقیقت","🎮 بازی‌ها","🎲 تاس","🪙 پرتاب سکه","🔢 حدس عدد","📝 حدس کلمه","🚩 حدس پرچم","✂️ سنگ کاغذ قیچی","⚔️ دوئل","🧠 تست هوش","🧩 معمای منطقی","🎲 بازی شانسی روزانه","🏆 مسابقه سرعت پاسخ","🌐 مترجم","🧮 ماشین حساب","⛅️ هواشناسی","📅 تاریخ و زمان","🔒 قفل‌های گروه","🔒 قفل‌ها","👋 خوشامدگویی","📜 قوانین","📊 آمار گروه","👤 مدیریت اعضا","⚙️ تنظیمات گروه","⚙️ تنظیمات عمومی","🤖 تنظیمات هوش مصنوعی","💰 تنظیمات اقتصاد","🛡 ضد اسپم","🆕 جلوگیری از ورود ربات","👤 محدودیت عضو جدید","⏳ تایید عضو جدید","📢 گزارش فعالیت","🔘 فعال/غیرفعال سازی خوشامدگویی","🔘 فعال/غیرفعال سازی قوانین","🔙 بازگشت به منوی اصلی","🔙 بازگشت به سرگرمی","🔙 بازگشت به مدیریت","🔙 بازگشت به مدیریت اعضا","🤝 پیوستن به بازی","🏁 شروع بازی","🔄 نوبت بعدی","🛑 توقف","جواب معما","جوابش","انصراف از بازی"}
def _looks_like_menu_button(text): return text.strip() in MENU_BUTTONS or text.strip().startswith("🔙 بازگشت")
async def ai_chat_handler(update,context):
    if not update.message or not update.message.text:return
    user=update.effective_user
    if not user or user.is_bot:return
    text=update.message.text.strip()
    if text.startswith("/") or _looks_like_menu_button(text):return
    chat_id=update.effective_chat.id; private=update.effective_chat.type=="private"; username=(context.bot.username or "").lower()
    if not (private or _sector_called(text,username) or _is_reply_to_this_bot(update,context)):return
    if not private:
        session=get_session(); group=session.query(Group).filter(Group.id==chat_id).first(); enabled=True if not group else group.ai_enabled; session.close()
        if not enabled:return
    query=re.sub(r"(?<![\w\u0600-\u06ff])(سکتور|sector)(?![\w\u0600-\u06ff])","",text,count=1,flags=re.I).strip(" ،,:؛;-") or text
    history=load_ai_history(chat_id)
    await update.effective_message.reply_chat_action("typing"); response=await get_ai_response(get_sector_prompt(user),query,use_search=needs_web_search(query),history=history)
    if not response: await update.effective_message.reply_text("الان به مدل هوش مصنوعی وصل نیستم 😅"); raise ApplicationHandlerStop()
    save_ai_turn(user.id,chat_id,query,response)
    await update.effective_message.reply_text(response[:4000]); raise ApplicationHandlerStop()
def get_handlers(): return [MessageHandler(filters.TEXT & ~filters.COMMAND,ai_chat_handler)]
