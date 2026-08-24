import datetime
import logging
import os
import time
from typing import Optional

from fastapi import Header, HTTPException
from telegram import Bot

from api.main import app, require_user
from bot.database.models import SectorClan, SectorClanMember, SectorPet, User
from bot.database.session import get_session
from bot.modules.ai import get_ai_response, load_ai_history, save_ai_turn
from bot.services import sector_pet as legacy
from bot.services import sector_v2

log = logging.getLogger(__name__)
REQUIRED_MEMBERSHIP_CHAT = os.getenv("REQUIRED_MEMBERSHIP_CHAT", "@sectorland")
_membership_cache = {}
_MEMBERSHIP_TTL = 75


async def _require_member(user_id: int):
    now = time.monotonic()
    cached = _membership_cache.get(user_id)
    if cached and now - cached[0] < _MEMBERSHIP_TTL:
        if cached[1]:
            return
        raise HTTPException(status_code=403, detail="عضویت در SectorLand الزامی است")
    token = (os.getenv("BOT_TOKEN") or "").strip()
    if not token:
        raise HTTPException(status_code=503, detail="Membership check unavailable")
    try:
        async with Bot(token=token) as bot:
            member = await bot.get_chat_member(REQUIRED_MEMBERSHIP_CHAT, user_id)
        status = getattr(member.status, "value", str(member.status))
        allowed = status in {"creator", "owner", "administrator", "member"}
        if status == "restricted":
            allowed = bool(getattr(member, "is_member", False))
        _membership_cache[user_id] = (now, bool(allowed))
        if not allowed:
            raise HTTPException(status_code=403, detail="عضویت در SectorLand الزامی است")
    except HTTPException:
        raise
    except Exception as exc:
        log.warning("Sector v2 membership check failed: %s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Membership check temporarily unavailable")


async def _guard(user_id: int, init_data: Optional[str]):
    require_user(init_data, user_id)
    await _require_member(user_id)


def _payload(session, user_id: int):
    now = datetime.datetime.utcnow()
    pet = legacy.get_or_create_pet(session, user_id, now)
    legacy.refresh_pet(pet, now)
    legacy.touch_daily_visit(pet, now)
    user = session.query(User).filter(User.id == user_id).first()
    coins=int(user.coins or 0) if user else 0
    daily=legacy.daily_progress(session, user_id, now)
    data = sector_v2.serialize_pet(pet, coins)
    data["guidance"]=legacy.progress_guidance(pet,daily,coins)
    membership = session.query(SectorClanMember).filter(SectorClanMember.user_id == user_id).first()
    clan = session.query(SectorClan).filter(SectorClan.id == membership.clan_id).first() if membership else None
    return {
        "pet": data,
        "daily": daily,
        "actions": [{"id": key, **value} for key, value in legacy.PET_ACTIONS.items()],
        "memories": legacy.list_memories(session, user_id, limit=50),
        "achievements": legacy.pet_achievements(session, pet),
        "shop": sector_v2.catalog_for(pet),
        "evolution_paths": legacy.EVOLUTION_PATHS,
        "jobs": legacy.JOBS,
        "story": legacy.STORY_CHAPTERS.get(int(pet.story_chapter or 1)),
        "clan": {"id": clan.id, "name": clan.name, "xp": int(clan.xp or 0), "contribution": int(membership.contribution or 0)} if clan else None,
    }


@app.get("/api/sector-v2/{user_id}")
async def get_sector_v2(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    session = get_session()
    try:
        payload = _payload(session, user_id)
        session.commit()
        return payload
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/action/{action}")
async def sector_v2_action(user_id: int, action: str, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    if action not in legacy.PET_ACTIONS:
        raise HTTPException(status_code=400, detail="اکشن نامعتبر است")
    session = get_session()
    try:
        result = sector_v2.perform_action(session, user_id, action)
        if result.get("status") == "success": session.commit()
        else: session.rollback()
        return result
    except Exception:
        session.rollback()
        log.exception("Sector v2 care action failed: %s", action)
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/rename")
async def sector_v2_rename(user_id: int, request: dict, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    name = " ".join(str(request.get("name") or "").strip().split())
    if not (2 <= len(name) <= 20):
        raise HTTPException(status_code=400, detail="نام سکتور باید بین ۲ تا ۲۰ نویسه باشد.")
    session = get_session()
    try:
        pet = legacy.get_or_create_pet(session, user_id, lock=True)
        old = pet.name
        pet.name = name
        pet.updated_at = datetime.datetime.utcnow()
        if old != name:
            legacy.remember(session, user_id, "identity", "تغییر نام", f"نام سکتور از {old} به {name} تغییر کرد.", 2)
        session.commit()
        return {"status":"success","message":"نام سکتور ذخیره شد.","pet":sector_v2.serialize_pet(pet)}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/minigame/{game_key}")
async def sector_v2_minigame(user_id: int, game_key: str, request: dict, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    try:
        score = int(request.get("score") or 0)
    except Exception:
        raise HTTPException(status_code=400, detail="امتیاز نامعتبر است")
    session = get_session()
    try:
        result = legacy.finish_minigame(session, user_id, game_key, score)
        if result.get("status") == "success":
            pet = legacy.get_or_create_pet(session, user_id)
            result["pet"] = sector_v2.serialize_pet(pet)
            result["daily"] = legacy.daily_progress(session, user_id)
            session.commit()
        else:
            session.rollback()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/social/{action}")
async def sector_v2_social(user_id: int, action: str, request: dict, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    target_raw = str(request.get("target") or "").strip().lstrip("@")
    if not target_raw:
        raise HTTPException(status_code=400, detail="کاربر مقصد را وارد کن")
    session = get_session()
    try:
        target = None
        if target_raw.isdigit():
            target = session.query(User).filter(User.id == int(target_raw)).first()
        if not target:
            target = session.query(User).filter(User.username.ilike(target_raw)).first()
        if not target:
            return {"status":"error","message":"کاربر مقصد پیدا نشد."}
        result = legacy.social_action(session, user_id, int(target.id), action)
        if result.get("status") == "success":
            session.commit()
            pet = legacy.get_or_create_pet(session, user_id)
            result["pet"] = sector_v2.serialize_pet(pet)
        else:
            session.rollback()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.get("/api/sector-v2/leaderboard/me/{user_id}")
async def sector_v2_leaderboard(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    session = get_session()
    try:
        rows = session.query(SectorPet, User).join(User, User.id == SectorPet.user_id).order_by(SectorPet.xp.desc()).limit(30).all()
        return [{"rank":i+1,"name":pet.name,"owner":user.first_name,"level":legacy.level_from_xp(pet.xp),"xp":int(pet.xp or 0),"path":pet.evolution_path} for i,(pet,user) in enumerate(rows)]
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/shop/{item_key}/buy")
async def sector_v2_buy(user_id: int, item_key: str, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    session = get_session()
    try:
        result = sector_v2.buy_item(session, user_id, item_key)
        if result.get("status") == "success": session.commit()
        else: session.rollback()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/shop/{item_key}/equip")
async def sector_v2_equip(user_id: int, item_key: str, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    session = get_session()
    try:
        result = sector_v2.equip_item(session, user_id, item_key)
        if result.get("status") == "success": session.commit()
        else: session.rollback()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/shop/slot/{slot}/unequip")
async def sector_v2_unequip(user_id: int, slot: str, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    session = get_session()
    try:
        result = sector_v2.unequip_slot(session, user_id, slot)
        if result.get("status") == "success": session.commit()
        else: session.rollback()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.post("/api/sector-v2/{user_id}/talk")
async def sector_v2_talk(user_id: int, request: dict, init_data: Optional[str] = Header(None, alias="init-data")):
    await _guard(user_id, init_data)
    message = str(request.get("message") or "").strip()
    if not message or len(message) > 700:
        raise HTTPException(status_code=400, detail="پیام باید بین ۱ تا ۷۰۰ نویسه باشد.")
    session = get_session()
    try:
        pet = legacy.get_or_create_pet(session, user_id)
        legacy.refresh_pet(pet)
        legacy.touch_daily_visit(pet)
        pet_data = sector_v2.serialize_pet(pet)
        memory_context = sector_v2.chat_context(session, user_id)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    stage = (pet_data.get("visual_stage") or {}).get("title", "Scrap Unit")
    mood = (pet_data.get("mood") or {}).get("title", "آرام")
    prompt = (
        f"تو خود سکتور کوچولوی این کاربر هستی. نامت «{pet_data['name']}» است و یک دستیار عمومی نیستی. "
        f"فرم فعلی بدنه‌ات {stage}، سطح {pet_data['level']} و حالتت {mood} است. "
        "در مراحل پایین کمی ساده، فرسوده و خام حرف بزن و با رشد سطح، دقیق‌تر و باهوش‌تر شو. "
        "پاسخ فارسی، طبیعی، کوتاه و شخصیت‌دار باشد. از لحن بچگانه و ایموجی‌باران دوری کن. "
        f"خاطرات مهم تو: {memory_context}"
    )
    try:
        history = load_ai_history(-user_id, 18)
    except Exception:
        log.exception("Unable to load Sector v2 AI history")
        history = []
    try:
        response = await get_ai_response(prompt, message, history=history)
    except Exception:
        log.exception("Sector v2 AI talk failed")
        response = None
    response = (response or sector_v2.local_chat_fallback(pet_data, message)).strip()[:2000]
    try:
        save_ai_turn(user_id, -user_id, message, response)
    except Exception:
        log.exception("Unable to save Sector v2 AI history")
    memory_session = get_session()
    try:
        sector_v2.remember_chat(memory_session, user_id, message, response)
        memory_session.commit()
    except Exception:
        memory_session.rollback()
        log.exception("Unable to save Sector v2 chat memory")
    finally:
        memory_session.close()
    return {"status": "success", "response": response, "pet": pet_data}
