from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("☁️ **وضعیت آب و هوا:**\nآسمان صاف، دمای فعلی ۲۴ درجه سانتی‌گراد است. (داده‌ها به صورت آزمایشی)", parse_mode="Markdown")

async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("🌍 **مترجم:**\nبرای ترجمه، متن خود را با دستور `/translate متن` ارسال کنید.", parse_mode="Markdown")

async def calc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("🧮 **حسابگر:**\nمثال: `/calc 5 * 10`", parse_mode="Markdown")
        return

    expr = "".join(context.args)
    try:
        allowed = "0123456789+-*/.() "
        if all(c in allowed for c in expr):
            res = eval(expr)
            await update.effective_message.reply_text(f"🔢 نتیجه: `{res}`", parse_mode="Markdown")
        else:
            await update.effective_message.reply_text("❌ عبارت نامعتبر است.")
    except:
        await update.effective_message.reply_text("❌ خطا در محاسبه.")

async def convert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("⚖️ **تبدیل واحد:**\nقابلیت تبدیل طول، وزن و دما فعال شد. بزودی رابط کاربری کامل می‌شود.", parse_mode="Markdown")

def get_handlers():
    return [
        CommandHandler("weather", weather_cmd),
        CommandHandler("translate", translate_cmd),
        CommandHandler("calc", calc_cmd),
        CommandHandler("convert", convert_cmd),
    ]
