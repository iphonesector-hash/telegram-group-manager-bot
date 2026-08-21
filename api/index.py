import os
import hmac
from fastapi import Request, HTTPException
from telegram import Update, Bot
from sqlalchemy import text

from api.main import app
from bot.main import build_application
from bot.database.session import engine


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "service": "isectorland-unified",
        "bot_configured": bool(os.getenv("BOT_TOKEN")),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "webhook_secret_configured": bool(os.getenv("TELEGRAM_WEBHOOK_SECRET")),
    }


@app.get("/api/setup-webhook")
async def setup_webhook(request: Request):
    configured = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    supplied = request.query_params.get("key", "")
    if not configured or not hmac.compare_digest(supplied, configured):
        raise HTTPException(status_code=401, detail="unauthorized")

    token = os.getenv("BOT_TOKEN", "")
    if not token or engine is None:
        raise HTTPException(status_code=503, detail="runtime not fully configured")

    with engine.connect() as conn:
        db_ok = conn.execute(text("select 1")).scalar() == 1

    webhook_url = "https://telegram-group-manager-bot-iota.vercel.app/api/telegram"
    bot = Bot(token=token)
    me = await bot.get_me()
    result = await bot.set_webhook(
        url=webhook_url,
        secret_token=configured,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
    )
    info = await bot.get_webhook_info()
    return {
        "ok": bool(result),
        "database_ok": db_ok,
        "bot": {"id": me.id, "username": me.username},
        "webhook": {
            "url": info.url,
            "pending_update_count": info.pending_update_count,
            "last_error_message": info.last_error_message,
        },
    }


@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    configured = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not configured:
        raise HTTPException(status_code=503, detail="webhook secret not configured")

    received = request.headers.get("x-telegram-bot-api-secret-token", "")
    if not hmac.compare_digest(received, configured):
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    if not os.getenv("BOT_TOKEN") or not os.getenv("DATABASE_URL"):
        raise HTTPException(status_code=503, detail="bot runtime not fully configured")

    payload = await request.json()
    telegram_app = build_application()
    await telegram_app.initialize()
    try:
        update = Update.de_json(payload, telegram_app.bot)
        await telegram_app.process_update(update)
    finally:
        await telegram_app.shutdown()

    return {"ok": True}
