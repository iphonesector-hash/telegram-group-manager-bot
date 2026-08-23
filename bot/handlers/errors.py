async def error_handler(update, context):
    print(f"⚠️ خطا: {context.error}")
    try:
        if update and update.callback_query:
            await update.callback_query.answer("این بخش موقتاً خطا داد؛ دوباره امتحان کن.",show_alert=True)
        elif update and update.effective_message:
            await update.effective_message.reply_text("⚠️ اجرای این بخش کامل نشد. خطا ثبت شد و در حال بررسی است.")
    except Exception:
        pass
