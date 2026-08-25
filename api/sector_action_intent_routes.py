"""Fast coherent Sector actions shared by Mini App care and natural-language chat.

These routes keep a single transaction for pet state + story readiness so the UI
never renders a fresh health/energy value beside a stale narrative objective.
"""
import re
from typing import Optional

from fastapi import Header, HTTPException

from api.main import app
from api.sector_v2_routes import _guard, sector_v2_talk
from bot.database.session import get_session
from bot.services import sector_pet as legacy
from bot.services import sector_story, sector_v2


_ACTION_PATTERNS = (
    ("train", (r"\bتمرین\b", r"تمرین کن", r"تمرین بده", r"ورزش", r"تمرین رزمی")),
    ("charge", (r"شارژ", r"انرژی.*پر", r"باتری.*پر")),
    ("repair", (r"تعمیر", r"درستت کن", r"خودت رو درست", r"بدنه.*تعمیر")),
    ("feed", (r"غذا", r"بخور", r"گرسنه")),
    ("clean", (r"تمیز", r"نظافت", r"بشور")),
    ("sleep", (r"استراحت", r"بخواب", r"خواب")),
    ("learn", (r"یاد بگیر", r"یادگیری", r"مطالعه")),
    ("play", (r"بازی کن", r"بازی کنیم")),
)


def _intent(message: str):
    normalized = " ".join(str(message or "").strip().lower().split())
    if not normalized:
        return None
    # Questions such as «تمرین چیه؟» should stay conversational. Commands and
    # direct requests are treated as real actions.
    questionish = any(token in normalized for token in ("چیه", "چیست", "چطور", "چگونه", "کجاست", "کدوم"))
    for action, patterns in _ACTION_PATTERNS:
        if any(re.search(pattern, normalized) for pattern in patterns):
            commandish = any(token in normalized for token in ("کن", "بده", "شو", "بخور", "بخواب", "بشور", "بگیریم", "بکن", "انجام"))
            if commandish or (not questionish and len(normalized) <= 32):
                return action
    return None


def _story_after_action(session, user_id: int, pet):
    before = sector_story.snapshot(session, user_id, pet)
    advanced = False
    advance_result = None
    if before.get("scene", {}).get("ready"):
        advance_result = sector_story.advance(session, user_id)
        advanced = advance_result.get("status") == "success"
    after_pet = legacy.get_or_create_pet(session, user_id)
    after = sector_story.snapshot(session, user_id, after_pet)
    return before, after, advanced, advance_result


def _perform(session, user_id: int, action: str):
    if action not in legacy.PET_ACTIONS:
        return {"status": "error", "message": "این فعالیت وجود ندارد."}
    result = sector_v2.perform_action(session, user_id, action)
    if result.get("status") != "success":
        return result
    pet = legacy.get_or_create_pet(session, user_id)
    before, narrative, advanced, story_result = _story_after_action(session, user_id, pet)
    pet = legacy.get_or_create_pet(session, user_id)
    result["pet"] = sector_v2.serialize_pet(pet, int(result.get("coins") or 0))
    result["daily"] = legacy.daily_progress(session, user_id)
    result["narrative"] = narrative
    result["story_advanced"] = advanced
    if advanced:
        next_text = narrative.get("scene", {}).get("objective") or "مرحله بعدی داستان آماده است."
        result["story_message"] = (story_result or {}).get("message")
        result["message"] = f"{result.get('message','انجام شد')} · هدف داستان کامل شد. حالا: {next_text}"
    elif before.get("scene", {}).get("requirements"):
        result["story_message"] = before["scene"].get("objective")
    return result


@app.post("/api/sector-v2/{user_id}/action-smart/{action}")
async def sector_smart_action(user_id: int, action: str, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    if action not in legacy.PET_ACTIONS:
        raise HTTPException(status_code=400, detail="فعالیت نامعتبر است")
    session = get_session()
    try:
        result = _perform(session, user_id, action)
        if result.get("status") == "success":
            session.commit()
        else:
            session.rollback()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/talk-smart")
async def sector_smart_talk(user_id: int, request: dict, init_data: Optional[str] = Header(None, alias="init-data")):
    message = str(request.get("message") or "").strip()
    action = _intent(message)
    if not action:
        return await sector_v2_talk(user_id, request, init_data)

    await _guard(user_id, init_data)
    session = get_session()
    try:
        result = _perform(session, user_id, action)
        if result.get("status") == "success":
            session.commit()
        else:
            session.rollback()
        if result.get("status") != "success":
            return {"status":"error","message":result.get("message") or "این کار انجام نشد."}
        pet = result.get("pet") or {}
        narrative = result.get("narrative") or {}
        scene = narrative.get("scene") or {}
        action_title = legacy.PET_ACTIONS.get(action, {}).get("title", "فعالیت")
        if result.get("story_advanced"):
            response = f"{action_title} انجام شد و هدف داستان هم کامل شد. قدم بعدی: {scene.get('objective','داستان را ادامه بده.')}"
        else:
            response = f"{action_title} واقعاً ثبت شد. {scene.get('objective') or result.get('message','')}"
        return {"status":"success","response":response,"pet":pet,"daily":result.get("daily"),"narrative":narrative,"action_executed":action,"story_advanced":bool(result.get("story_advanced"))}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
