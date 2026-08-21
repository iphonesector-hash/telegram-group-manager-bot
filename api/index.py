import os
import hmac
import psycopg2
from fastapi import Request, HTTPException
from telegram import Update, Bot
from sqlalchemy import text
from sqlalchemy.engine import make_url

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


async def _application_self_test():
    test = {"ok": False}
    telegram_app = None
    try:
        telegram_app = build_application()
        await telegram_app.initialize()
        test["initialized"] = True
        fake = Update.de_json({"update_id": 999999999}, telegram_app.bot)
        await telegram_app.process_update(fake)
        test["processed"] = True
        test["ok"] = True
    except Exception as exc:
        test["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if telegram_app is not None:
            try:
                await telegram_app.shutdown()
            except Exception as exc:
                test["shutdown_error"] = f"{type(exc).__name__}: {exc}"
    return test


@app.get("/api/setup-webhook")
async def setup_webhook(request: Request):
    configured = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    supplied = request.query_params.get("key", "")
    if not configured or not hmac.compare_digest(supplied, configured):
        raise HTTPException(status_code=401, detail="unauthorized")

    token = os.getenv("BOT_TOKEN", "")
    raw_db = os.getenv("DATABASE_URL", "")
    if not token or not raw_db:
        raise HTTPException(status_code=503, detail="runtime not fully configured")

    result = {"ok": False, "database_ok": False, "telegram_ok": False}

    try:
        with engine.connect() as conn:
            result["database_ok"] = conn.execute(text("select 1")).scalar() == 1
    except Exception as exc:
        result["database_error"] = f"{type(exc).__name__}: {exc}"

        parsed = make_url(raw_db.replace("postgres://", "postgresql://", 1))
        direct_host = parsed.host or ""
        project_ref = direct_host.split(".")[1] if direct_host.startswith("db.") else ""
        probe = []
        if project_ref and parsed.password:
            for idx in range(0, 6):
                host = f"aws-{idx}-eu-west-1.pooler.supabase.com"
                try:
                    conn = psycopg2.connect(
                        host=host,
                        port=6543,
                        dbname=parsed.database or "postgres",
                        user=f"postgres.{project_ref}",
                        password=parsed.password,
                        connect_timeout=3,
                        sslmode="require",
                    )
                    cur = conn.cursor(); cur.execute("select 1"); ok = cur.fetchone()[0] == 1
                    cur.close(); conn.close()
                    probe.append({"host": host, "ok": ok})
                    if ok:
                        result["working_pooler_host"] = host
                        break
                except Exception as pexc:
                    probe.append({"host": host, "ok": False, "error": str(pexc).split("\n")[0][:180]})
        result["pooler_probe"] = probe
        if not result.get("working_pooler_host"):
            result["application_self_test"] = await _application_self_test()
            return result

    result["application_self_test"] = await _application_self_test()

    try:
        webhook_url = "https://telegram-group-manager-bot-iota.vercel.app/api/telegram"
        bot = Bot(token=token)
        me = await bot.get_me()
        set_result = await bot.set_webhook(
            url=webhook_url,
            secret_token=configured,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )
        info = await bot.get_webhook_info()
        result.update({
            "ok": bool(set_result) and bool(result["application_self_test"].get("ok")),
            "telegram_ok": True,
            "bot": {"id": me.id, "username": me.username},
            "webhook": {
                "url": info.url,
                "pending_update_count": info.pending_update_count,
                "last_error_message": info.last_error_message,
            },
        })
    except Exception as exc:
        result["telegram_error"] = f"{type(exc).__name__}: {exc}"
    return result


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
