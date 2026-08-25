"""Shared cached Telegram Premium emoji helpers for Sector Koochooloo.

The dedicated Sector Koochooloo library is intentionally separate from the
older bot-wide Sector emoji setting. Existing emoji data is never deleted.
"""
import time

from bot.database.models import AppSetting
from bot.database.session import get_session

SECTOR_KOOCHOOLOO_EMOJI_KEY = "sector_koochooloo_custom_emoji_ids"
LEGACY_SECTOR_EMOJI_KEY = "sector_custom_emoji_id"
_CACHE = {"ids": [], "at": 0.0}
_TTL_SECONDS = 300


def _read_ids(session, key, limit=32):
    row = session.query(AppSetting).filter(AppSetting.key == key).first()
    raw = row.value if row and row.value else []
    values = raw if isinstance(raw, list) else [raw]
    return list(dict.fromkeys(str(value) for value in values if str(value).isdigit()))[:limit]


def get_sector_emoji_ids(force: bool = False):
    """Return Koochooloo's dedicated emoji library, with legacy fallback only.

    Once at least one dedicated emoji exists, no legacy emoji is mixed into the
    active library. This keeps the new visual identity clean without deleting
    any older saved emoji configuration.
    """
    now = time.monotonic()
    if not force and now - float(_CACHE.get("at") or 0) < _TTL_SECONDS:
        return list(_CACHE.get("ids") or [])
    try:
        session = get_session()
    except Exception:
        return list(_CACHE.get("ids") or [])
    try:
        dedicated = _read_ids(session, SECTOR_KOOCHOOLOO_EMOJI_KEY)
        ids = dedicated or _read_ids(session, LEGACY_SECTOR_EMOJI_KEY, limit=16)
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
