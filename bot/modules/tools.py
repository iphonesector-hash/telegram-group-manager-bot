from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("☁️ **وضعیت آب و هوا:**\nدر حال حاضر سرویس در حال بروزرسانی است. لطفاً بعداً تلاش کنید.", parse_mode="Markdown")

async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("🌍 **مترجم هوشمند:**\nمتن خود را برای ترجمه ارسال کنید (بزودی فعال می‌شود).", parse_mode="Markdown")

async def calc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("🧮 **حسابگر:**\nمثال: `/calc 2 + 2`", parse_mode="Markdown")
        return

    expr = "".join(context.args)
    try:
        # Simple evaluation for basic math
        allowed = "0123456789+-*/.() "
        if all(c in allowed for c in expr):
            res = eval(expr)
            await update.effective_message.reply_text(f"🔢 نتیجه: `{res}`", parse_mode="Markdown")
        else:
            await update.effective_message.reply_text("❌ عبارت نامعتبر است.")
    except:
        await update.effective_message.reply_text("❌ خطا در محاسبه.")

def get_handlers():
    return [
        CommandHandler("weather", weather_cmd),
        CommandHandler("translate", translate_cmd),
        CommandHandler("calc", calc_cmd),
    ]
