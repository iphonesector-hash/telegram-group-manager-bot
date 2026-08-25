"""Safe Mini App diagnostics and owner runtime health for SectorLand."""
import datetime
import logging
import re
from typing import Optional

from fastapi import Header, HTTPException, Request
from sqlalchemy import func, text

from api.main import app, require_user
from bot.database.models import RuntimeState, SectorPetAction, SectorPetGame
from bot.database.session import get_session
from bot.utils.helpers import OWNER_ID

log = logging.getLogger(__name__)


def _clean(value, limit):
    value = str(value or "")
    # Strip common Telegram init-data/token-shaped values if a browser error
    # accidentally embeds them in a stack/message.
    value = re.sub(r"(query_id|hash|auth_date|user|init-data)=([^\s&]+)", r"\1=[redacted]", value, flags=re.I)
    value = re.sub(r"bot\d+:[A-Za-z0-9_-]{20,}", "bot[redacted]", value, flags=re.I)
    return value[:limit]


@app.post("/api/miniapp-diagnostic-v2")
async def miniapp_diagnostic_v2(request: Request, init_data: Optional[str] = Header(None, alias="init-data")):
    telegram_user = require_user(init_data)
    data = await request.json()
    user_id = int(telegram_user.get("id") or 0)
    safe = {
        "phase": _clean(data.get("phase"), 80),
        "version": _clean(data.get("version"), 100),
        "platform": _clean(data.get("platform"), 40),
        "message": _clean(data.get("message"), 500),
        "stack": _clean(data.get("stack"), 3500),
        "path": _clean(data.get("path"), 180),
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    log.warning("MiniApp diagnostic v2 phase=%s version=%s platform=%s message=%s stack=%s", safe["phase"], safe["version"], safe["platform"], safe["message"], safe["stack"])
    session = get_session()
    try:
        key = f"latest:{user_id}"
        row = session.query(RuntimeState).filter_by(scope="miniapp_diagnostic_v2", state_key=key).first()
        if row:
            previous = dict(row.value or {})
            safe["count"] = int(previous.get("count") or 0) + 1
            row.value = safe
            row.updated_at = datetime.datetime.utcnow()
        else:
            safe["count"] = 1
            session.add(RuntimeState(scope="miniapp_diagnostic_v2", state_key=key, value=safe, updated_at=datetime.datetime.utcnow()))
        session.commit()
    except Exception:
        session.rollback()
        log.exception("Unable to persist Mini App diagnostic")
    finally:
        session.close()
    return {"ok": True}


@app.get("/api/sector-runtime-admin/{user_id}")
async def sector_runtime_admin(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    if int(user_id) != int(OWNER_ID):
        raise HTTPException(status_code=403, detail="Owner only")
    session = get_session()
    try:
        now = datetime.datetime.utcnow()
        day = now - datetime.timedelta(hours=24)
        actions = session.query(SectorPetAction).filter(SectorPetAction.created_at >= day)
        games = session.query(SectorPetGame).filter(SectorPetGame.created_at >= day)
        active_users = session.query(func.count(func.distinct(SectorPetAction.user_id))).filter(SectorPetAction.created_at >= day).scalar() or 0
        diagnostics = session.query(RuntimeState).filter(RuntimeState.scope == "miniapp_diagnostic_v2").order_by(RuntimeState.updated_at.desc()).limit(8).all()
        db_ok = session.execute(text("select 1")).scalar() == 1
        return {
            "ok": True,
            "database_ok": bool(db_ok),
            "server_time": now.isoformat(),
            "window_hours": 24,
            "care_actions": int(actions.count()),
            "games_finished": int(games.count()),
            "active_sector_users": int(active_users),
            "recent_client_crashes": [
                {
                    "phase": (row.value or {}).get("phase"),
                    "version": (row.value or {}).get("version"),
                    "platform": (row.value or {}).get("platform"),
                    "message": (row.value or {}).get("message"),
                    "stack": (row.value or {}).get("stack"),
                    "count": int((row.value or {}).get("count") or 1),
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                }
                for row in diagnostics
            ],
        }
    finally:
        session.close()
