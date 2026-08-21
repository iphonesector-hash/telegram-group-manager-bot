import os
import hmac
from fastapi import Request, HTTPException
from telegram import Update

from api.main import app
from bot.main import build_application


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "service": "isectorland-unified",
        "bot_configured": bool(os.getenv("BOT_TOKEN")),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "webhook_secret_configured": bool(os.getenv("TELEGRAM_WEBHOOK_SECRET")),
    }


@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    configured = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    received = request.headers.get("x-telegram-bot-api-secret-token", "")
    if configured and not hmac.compare_digest(received, configured):
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    payload = await request.json()
    telegram_app = build_application()
    await telegram_app.initialize()
    try:
        update = Update.de_json(payload, telegram_app.bot)
        await telegram_app.process_update(update)
    finally:
        await telegram_app.shutdown()

    return {"ok": True}
