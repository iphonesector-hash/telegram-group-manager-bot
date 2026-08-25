"""Shared cached Telegram Premium emoji helpers for SectorLand chat UI."""
import time

from bot.database.models import AppSetting
from bot.database.session import get_session

_CACHE = {"ids": [], "at": 0.0}
_TTL_SECONDS = 300


def get_sector_emoji_ids(force: bool = False):
    now = time.monotonic()
    if not force and now - float(_CACHE.get("at") or 0) < _TTL_SECONDS:
        return list(_CACHE.get("ids") or [])
    try:
        session = get_session()
    except Exception:
        return list(_CACHE.get("ids") or [])
    try:
        row = session.query(AppSetting).filter(AppSetting.key == "sector_custom_emoji_id").first()
        raw = row.value if row and row.value else []
        values = raw if isinstance(raw, list) else [raw]
        ids = [str(value) for value in values if str(value).isdigit()][:16]
        _CACHE["ids"] = ids
        _CACHE["at"] = now
        return list(ids)
    except Exception:
        return list(_CACHE.get("ids") or [])
    finally:
        session.close()


def animated_emoji(index: int, fallback: str):
    ids = get_sector_emoji_ids()
    if not ids:
        return fallback
    return f'<tg-emoji emoji-id="{ids[index % len(ids)]}">{fallback}</tg-emoji>'


def invalidate_sector_emoji_cache():
    _CACHE["at"] = 0.0
