"""Coherent Sector mutation responses.

Most Mini App actions used to require a second GET (and sometimes a third story
advance request) after a successful mutation.  These wrappers enrich successful
mutations inside the same database transaction with the fresh pet, economy and
narrative state.  Client refreshes then resolve from the short-lived snapshot
cache instead of waiting on another server round-trip.
"""
from functools import wraps

from bot.database.models import User
from bot.services import sector_expansion, sector_meta, sector_pet as legacy, sector_story, sector_v2

_PATCHED = False


def _fresh_state(session, user_id: int, result: dict):
    if not isinstance(result, dict) or result.get("status") != "success":
        return result

    pet = legacy.get_or_create_pet(session, user_id)
    narrative = sector_story.snapshot(session, user_id, pet)
    story_result = None
    if (narrative.get("scene") or {}).get("ready"):
        story_result = sector_story.advance(session, user_id)
        if story_result.get("status") == "success":
            pet = legacy.get_or_create_pet(session, user_id)
            narrative = sector_story.snapshot(session, user_id, pet)
            result["story_advanced"] = True
            result["story_message"] = story_result.get("message")

    user = session.query(User).filter(User.id == user_id).first()
    coins = int(user.coins or 0) if user else int(result.get("coins") or 0)
    result["coins"] = coins
    result["pet"] = sector_v2.serialize_pet(pet, coins)
    result["daily"] = legacy.daily_progress(session, user_id)
    result["narrative"] = narrative
    result["shop"] = sector_v2.catalog_for(pet)
    result["expansion"] = sector_expansion.snapshot(session, user_id)
    if result.get("story_advanced"):
        next_objective = (narrative.get("scene") or {}).get("objective")
        if next_objective:
            base = str(result.get("message") or "عملیات انجام شد.")
            result["message"] = f"{base} · هدف داستان کامل شد. حالا: {next_objective}"
    return result


def _wrap(service, name, user_arg=1):
    original = getattr(service, name, None)
    if not callable(original) or getattr(original, "_sector_coherent", False):
        return

    @wraps(original)
    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        try:
            session = args[0]
            user_id = int(args[user_arg])
            return _fresh_state(session, user_id, result)
        except Exception:
            # Never turn a successful domain operation into a server error only
            # because response enrichment failed. The client can still refresh.
            return result

    wrapped._sector_coherent = True
    setattr(service, name, wrapped)


def apply_sector_coherence():
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    for name in ("buy_item", "equip_item", "unequip_slot"):
        _wrap(sector_v2, name)
    for name in ("command", "tactical_battle"):
        _wrap(sector_expansion, name)
    for name in ("social_action", "finish_minigame", "choose_evolution"):
        _wrap(legacy, name)
    for name in ("attack_boss", "sell_item"):
        _wrap(sector_meta, name)


apply_sector_coherence()
