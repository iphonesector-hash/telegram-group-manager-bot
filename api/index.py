import os
import hmac
import logging
import base64
import asyncio
import psycopg2
from fastapi import Request, HTTPException, Header
from telegram import Update, Bot, WebAppInfo, MenuButtonWebApp
from sqlalchemy import text
from sqlalchemy.engine import make_url
from typing import Optional

# python-telegram-bot uses httpx internally.  INFO logs include the complete
# Bot API request URL, whose path contains the bot token.  Keep operational
# logs useful without leaking credentials into Vercel logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram.request").setLevel(logging.WARNING)

from api.main import app, require_user, serialize_purchase, serialize_order
from bot.main import build_application
from bot.database.session import engine, get_session, init_db
from bot.database.models import Purchase, Order

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://isectorland-miniapp.vercel.app")
BOT_BUILD = "2026.08.24-fast-keyboard"
REQUIRED_MEMBERSHIP_CHAT = os.getenv("REQUIRED_MEMBERSHIP_CHAT", "@sectorland")
REQUIRED_MEMBERSHIP_URL = os.getenv("REQUIRED_MEMBERSHIP_URL", "https://t.me/sectorland")
_menu_registered = False
_telegram_app = None
_telegram_app_lock = asyncio.Lock()
_database_ready = False
OWNER_ID = int(os.getenv("OWNER_ID", "5147526780"))


async def _register_default_menu(bot: Bot) -> bool:
    button = MenuButtonWebApp(text="sector", web_app=WebAppInfo(url=MINI_APP_URL))
    await bot.set_chat_menu_button(menu_button=button)
    # The owner had an older per-chat override. Per-chat values take priority
    # over the default menu, so keep the commander's launcher in sync too.
    await bot.set_chat_menu_button(chat_id=OWNER_ID, menu_button=button)
    return True


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "service": "isectorland-unified",
        "build": BOT_BUILD,
        "bot_configured": bool(os.getenv("BOT_TOKEN")),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "webhook_secret_configured": bool(os.getenv("TELEGRAM_WEBHOOK_SECRET")),
        "mini_app_url": MINI_APP_URL,
    }


@app.get("/api/membership/{user_id}")
async def miniapp_membership(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    """Require @sectorland membership before the Mini App unlocks."""
    require_user(init_data, user_id)
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise HTTPException(status_code=503, detail="Membership check unavailable")
    try:
        async with Bot(token=token) as bot:
            member = await bot.get_chat_member(REQUIRED_MEMBERSHIP_CHAT, user_id)
        status = getattr(member.status, "value", str(member.status))
        allowed = status in {"creator", "owner", "administrator", "member"}
        if status == "restricted":
            allowed = bool(getattr(member, "is_member", False))
        return {
            "required": True,
            "member": bool(allowed),
            "chat": REQUIRED_MEMBERSHIP_CHAT,
            "url": REQUIRED_MEMBERSHIP_URL,
            "status": status,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logging.getLogger(__name__).warning("Mini App membership check failed: %s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Membership check temporarily unavailable")


@app.get("/api/miniapp-status")
async def miniapp_status(init_data: Optional[str] = Header(None, alias="init-data")):
    """Read the launcher configuration currently stored by Telegram."""
    user = require_user(init_data)
    if int(user.get("id", 0)) != OWNER_ID:
        raise HTTPException(status_code=403, detail="admin access required")
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise HTTPException(status_code=503, detail="bot token not configured")
    async with Bot(token=token) as bot:
        default_button = await bot.get_chat_menu_button()
        owner_button = await bot.get_chat_menu_button(chat_id=OWNER_ID)
        def info(button):
            web_app = getattr(button, "web_app", None)
            return {"type": button.type, "text": getattr(button, "text", None), "url": getattr(web_app, "url", None)}
        return {"expected_url": MINI_APP_URL, "default": info(default_button), "owner": info(owner_button)}


@app.post("/api/miniapp-diagnostic")
async def miniapp_diagnostic(request: Request, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data)
    data = await request.json()
    # No Telegram initData or personal information is logged here.
    safe = {key: data.get(key) for key in ("bridge", "user", "init", "version", "platform", "phase")}
    logging.getLogger(__name__).warning("MiniApp diagnostic: %s", safe)
    return {"ok": True}


@app.get("/api/user-photo/{user_id}")
async def user_photo(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        return {"photo_url": None}
    try:
        async with Bot(token=token) as bot:
            photos = await bot.get_user_profile_photos(user_id=user_id, limit=1)
            if not photos.photos:
                return {"photo_url": None}
            telegram_file = await bot.get_file(photos.photos[0][-1].file_id)
            payload = bytes(await telegram_file.download_as_bytearray())
            if len(payload) > 1_500_000:
                return {"photo_url": None}
            encoded = base64.b64encode(payload).decode("ascii")
            return {"photo_url": "data:image/jpeg;base64," + encoded}
    except Exception:
        logging.getLogger(__name__).warning("Unable to load Telegram profile photo for user %s", user_id)
        return {"photo_url": None}


async def miniapp_orders(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        rows = (
            session.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(50)
            .all()
        )
        return [serialize_order(order) for order in rows]
    finally:
        session.close()


async def miniapp_transactions(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        rows = (
            session.query(Purchase)
            .filter(Purchase.user_id == user_id)
            .order_by(Purchase.created_at.desc())
            .limit(60)
            .all()
        )
        result = []
        for p in rows:
            raw = serialize_purchase(p)
            status = p.status or ""
            item_id = p.item_id or ""
            amount = int(p.amount or 0)
            positive = status in ("reward", "quiz_correct") or item_id in ("loan", "bank_withdraw")
            if status == "coin_purchase" or item_id in ("bank_deposit", "loan_repay"):
                positive = False
            labels = {
                "daily_reward": "هدیه روزانه",
                "bank_deposit": "واریز به بانک",
                "bank_withdraw": "برداشت از بانک",
                "loan": "دریافت وام",
                "loan_repay": "تسویه وام",
            }
            if str(item_id).startswith("intel-") or str(item_id).startswith("logic-") or str(item_id).startswith("flag-"):
                label = "پاداش پاسخ صحیح" if status == "quiz_correct" else "پاسخ مسابقه"
            else:
                label = labels.get(item_id, raw.get("name") or str(item_id))
            result.append({
                "id": p.id,
                "label": label,
                "amount": amount if positive else -amount,
                "status": status,
                "date": p.created_at.isoformat() if p.created_at else None,
            })
        return result
    finally:
        session.close()


async def _application_self_test():
    test = {"ok": False}
    telegram_app = None
    try:
        telegram_app = build_application(initialize_database=False)
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


@app.post("/api/setup-webhook")
async def setup_webhook(request: Request):
    configured = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    supplied = request.headers.get("x-setup-secret", "")
    if not configured or not hmac.compare_digest(supplied, configured):
        raise HTTPException(status_code=401, detail="unauthorized")

    token = os.getenv("BOT_TOKEN", "")
    raw_db = os.getenv("DATABASE_URL", "")
    if not token or not raw_db:
        raise HTTPException(status_code=503, detail="runtime not fully configured")

    result = {"ok": False, "database_ok": False, "telegram_ok": False, "menu_registered": False}

    try:
        # Explicit maintenance operation: schema changes happen here, never in
        # the user-facing webhook request path.
        await asyncio.to_thread(init_db)
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
        webhook_url = f"{MINI_APP_URL.rstrip('/')}/api/telegram"
        bot = Bot(token=token)
        me = await bot.get_me()
        result["menu_registered"] = await _register_default_menu(bot)
        set_result = await bot.set_webhook(
            url=webhook_url,
            secret_token=configured,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )
        info = await bot.get_webhook_info()
        result.update({
            "ok": bool(set_result) and bool(result["application_self_test"].get("ok")) and bool(result["menu_registered"]),
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


async def _get_telegram_application():
    """Return one initialized PTB application per warm serverless instance."""
    global _telegram_app, _database_ready
    if _telegram_app is not None:
        return _telegram_app
    async with _telegram_app_lock:
        if _telegram_app is not None:
            return _telegram_app
        if not _database_ready:
            await asyncio.to_thread(init_db)
            _database_ready = True
        app_instance = build_application(initialize_database=False)
        await app_instance.initialize()
        _telegram_app = app_instance
        return _telegram_app


@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    global _menu_registered

    configured = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not configured:
        raise HTTPException(status_code=503, detail="webhook secret not configured")

    received = request.headers.get("x-telegram-bot-api-secret-token", "")
    if not hmac.compare_digest(received, configured):
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    if not os.getenv("BOT_TOKEN") or not os.getenv("DATABASE_URL"):
        raise HTTPException(status_code=503, detail="bot runtime not fully configured")

    payload = await request.json()
    telegram_app = await _get_telegram_application()
    if not _menu_registered:
        try:
            _menu_registered = await _register_default_menu(telegram_app.bot)
        except Exception as exc:
            logging.getLogger(__name__).warning("Default menu registration failed: %s", type(exc).__name__)

    update = Update.de_json(payload, telegram_app.bot)
    await telegram_app.process_update(update)

    return {"ok": True}
