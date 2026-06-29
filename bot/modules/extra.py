import random
import re
import datetime
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from bot.utils.helpers import is_admin
from bot.modules.ai import get_ai_response

async def translator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    print(f"[TRACE] extra:translator_handler | text: {text}")
    if not text or not text.startswith("ترجمه:"): return
    query = text.replace("ترجمه:", "").strip()
    if not query: return
    await update.effective_message.reply_chat_action("typing")
    res = await get_ai_response("Translate the following text to Persian if it's English, or to English if it's Persian. Only return the translation.", query)

    if res:
        await update.effective_message.reply_text(f"🌐 ترجمه:\n\n{res}", parse_mode=None)
    else:
        await update.effective_message.reply_text("❌ خطا در ترجمه. لطفاً دوباره تلاش کنید.")
    print(f"[TRACE] extra:translator_handler | handled | ApplicationHandlerStop")
    raise ApplicationHandlerStop()

async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    print(f"[TRACE] extra:weather_handler | text: {text}")
    if not text or not text.startswith("هوای "): return
    city = text.replace("هوای ", "").strip()
    if not city: return
    await update.effective_message.reply_chat_action("typing")
    res = await get_ai_response(f"Get the current weather for {city}. Respond in Persian with temperature and condition.", f"Weather in {city}", use_search=True)

    if res:
        await update.effective_message.reply_text(f"⛅️ وضعیت هوا:\n\n{res}", parse_mode=None)
    else:
        await update.effective_message.reply_text("❌ خطا در دریافت اطلاعات هواشناسی.")
    print(f"[TRACE] extra:weather_handler | handled | ApplicationHandlerStop")
    raise ApplicationHandlerStop()

async def calculator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    print(f"[TRACE] extra:calculator_handler | text: {text}")
    if not text or not re.match(r"^[0-9\s\+\-\*\/\(\)\.]+$", text): return
    if len(text) < 3: return
    try:
        res = await get_ai_response("Calculate this math expression and return only the numeric result.", text)
        if res:
            await update.effective_message.reply_text(f"🧮 نتیجه: {res}", parse_mode=None)
            print(f"[TRACE] extra:calculator_handler | handled | ApplicationHandlerStop")
            raise ApplicationHandlerStop()
    except ApplicationHandlerStop: raise
    except: pass

async def general_utils_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    print(f"[TRACE] extra:general_utils_handler | text: {text}")
    if text == "🌐 مترجم":
        await update.effective_message.reply_text("🌐 برای ترجمه بنویسید:\nترجمه: [متن]")
    elif text == "🧮 ماشین حساب":
        await update.effective_message.reply_text("🧮 عبارت ریاضی خود را بفرستید (مثلا: 10 + 5)")
    elif text == "⛅️ هواشناسی":
        await update.effective_message.reply_text("⛅️ بنویسید: هوای [نام شهر]")
    elif text == "📅 تاریخ و زمان":
        now = datetime.datetime.now()
        await update.effective_message.reply_text(f"📅 تاریخ: {now.strftime('%Y-%m-%d')}\n🕒 زمان: {now.strftime('%H:%M:%S')}")
    else:
        return
    print(f"[TRACE] extra:general_utils_handler | handled | ApplicationHandlerStop")
    raise ApplicationHandlerStop()

def get_extra_handlers():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^(🌐 مترجم|🧮 ماشین حساب|⛅️ هواشناسی|📅 تاریخ و زمان)$"), general_utils_handler),
        MessageHandler(filters.TEXT & filters.Regex("^ترجمه:"), translator_handler),
        MessageHandler(filters.TEXT & filters.Regex("^هوای "), weather_handler),
        MessageHandler(filters.TEXT & filters.Regex(r"^[0-9\s\+\-\*\/\(\)\.]+$"), calculator_handler),
    ]
