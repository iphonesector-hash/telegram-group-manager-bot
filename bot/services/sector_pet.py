import datetime
import math
import random

from bot.database.models import SectorPet, SectorPetAction, User
from bot.utils.helpers import OWNER_ID


PET_ACTIONS = {
    "charge": {"title": "شارژ انرژی", "icon": "⚡", "cost": 20, "xp": 10, "energy": 30, "happiness": 3, "knowledge": 0, "health": 3},
    "play": {"title": "بازی", "icon": "🎮", "cost": 15, "xp": 15, "energy": -8, "happiness": 25, "knowledge": 1, "health": 0},
    "train": {"title": "تمرین", "icon": "🏋️", "cost": 30, "xp": 30, "energy": -18, "happiness": 5, "knowledge": 5, "health": 1},
    "learn": {"title": "یادگیری", "icon": "🧠", "cost": 40, "xp": 40, "energy": -12, "happiness": 2, "knowledge": 12, "health": 0},
    "repair": {"title": "تعمیر", "icon": "🔧", "cost": 60, "xp": 15, "energy": 5, "happiness": 4, "knowledge": 0, "health": 35},
}


def xp_for_level(level: int) -> int:
    """Cumulative XP curve: progression stays useful for many months."""
    level = max(1, min(100, int(level)))
    return int(85 * ((level - 1) ** 1.72))


def level_from_xp(xp: int) -> int:
    xp = max(0, int(xp or 0))
    level = 1
    while level < 100 and xp >= xp_for_level(level + 1):
        level += 1
    return level


def stage_for(level: int, care_days: int) -> dict:
    gates = (
        (4, 60, 150, "سکتور همه‌چیزدان"),
        (3, 30, 60, "سکتور حرفه‌ای"),
        (2, 10, 14, "سکتور کنجکاو"),
    )
    for stage_id, need_level, need_days, title in gates:
        if level >= need_level and care_days >= need_days:
            next_gate = None if stage_id == 4 else ({2: {"level": 30, "care_days": 60}, 3: {"level": 60, "care_days": 150}}[stage_id])
            return {"id": stage_id, "title": title, "next_gate": next_gate}
    return {"id": 1, "title": "سکتور کوچولو", "next_gate": {"level": 10, "care_days": 14}}


def get_or_create_pet(session, user_id: int, now=None, lock=False):
    now = now or datetime.datetime.utcnow()
    query = session.query(SectorPet).filter(SectorPet.user_id == user_id)
    if lock:
        query = query.with_for_update()
    pet = query.first()
    if not pet:
        pet = SectorPet(user_id=user_id, last_interaction=now, created_at=now, updated_at=now)
        session.add(pet)
        session.flush()
    return pet


def touch_daily_visit(pet: SectorPet, now=None):
    now = now or datetime.datetime.utcnow()
    today = now.date()
    last = pet.last_visit_date
    if last == today:
        return False
    pet.streak_days = int(pet.streak_days or 0) + 1 if last == today - datetime.timedelta(days=1) else 1
    pet.best_streak = max(int(pet.best_streak or 0), pet.streak_days)
    pet.total_care_days = int(pet.total_care_days or 0) + 1
    pet.last_visit_date = today
    pet.updated_at = now
    return True


def refresh_pet(pet: SectorPet, now=None):
    now = now or datetime.datetime.utcnow()
    last = pet.last_interaction.replace(tzinfo=None) if pet.last_interaction and pet.last_interaction.tzinfo else pet.last_interaction
    hours = max(0, int((now - (last or now)).total_seconds() // 3600))
    if hours:
        pet.energy = max(0, int(pet.energy or 0) - min(40, hours * 2))
        pet.happiness = max(0, int(pet.happiness or 0) - min(30, hours))
        if pet.energy == 0 or pet.happiness == 0:
            pet.health = max(20, int(pet.health or 100) - min(20, hours))
        pet.last_interaction = now
        pet.updated_at = now


def daily_progress(session, user_id: int, now=None):
    now = now or datetime.datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    count = session.query(SectorPetAction).filter(SectorPetAction.user_id == user_id, SectorPetAction.created_at >= start).count()
    return {"actions": count, "target": 3, "complete": count >= 3, "full_xp_remaining": max(0, 5 - count)}


def serialize_pet(pet: SectorPet):
    level = level_from_xp(pet.xp)
    pet.level = level
    floor = xp_for_level(level)
    ceiling = xp_for_level(min(100, level + 1))
    care_days = int(pet.total_care_days or 0)
    return {
        "name": pet.name, "level": level, "xp": int(pet.xp or 0),
        "xp_in_level": int(pet.xp or 0) - floor,
        "xp_next": max(1, ceiling - floor),
        "energy": int(pet.energy or 0), "happiness": int(pet.happiness or 0),
        "knowledge": int(pet.knowledge or 0), "health": int(pet.health or 0),
        "streak_days": int(pet.streak_days or 0), "best_streak": int(pet.best_streak or 0),
        "total_care_days": care_days, "evolution_tokens": int(pet.evolution_tokens or 0),
        "stage": stage_for(level, care_days),
    }


def perform_action(session, user_id: int, action: str, now=None):
    definition = PET_ACTIONS.get(action)
    if not definition:
        return {"status": "error", "message": "این فعالیت پیدا نشد."}
    now = now or datetime.datetime.utcnow()
    user = session.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        return {"status": "error", "message": "ابتدا /start را بزن تا حسابت ساخته شود."}
    last = session.query(SectorPetAction).filter(SectorPetAction.user_id == user_id).order_by(SectorPetAction.created_at.desc()).first()
    last_at = last.created_at.replace(tzinfo=None) if last and last.created_at and last.created_at.tzinfo else (last.created_at if last else None)
    if last_at and (now - last_at).total_seconds() < 3:
        return {"status": "error", "message": "سکتور سه ثانیه استراحت می‌خواهد؛ دوباره بزن."}
    pet = get_or_create_pet(session, user_id, now, lock=True)
    refresh_pet(pet, now)
    touch_daily_visit(pet, now)
    progress = daily_progress(session, user_id, now)
    cost = int(definition["cost"])
    if user_id != OWNER_ID and int(user.coins or 0) < cost:
        return {"status": "error", "message": "برای این کار سکه کافی نداری."}
    if user_id != OWNER_ID:
        user.coins = int(user.coins or 0) - cost
    gained_xp = int(definition["xp"] if progress["actions"] < 5 else max(2, math.ceil(definition["xp"] * .2)))
    for field in ("energy", "happiness", "knowledge", "health"):
        setattr(pet, field, max(0, min(100, int(getattr(pet, field) or 0) + int(definition[field]))))
    pet.xp = int(pet.xp or 0) + gained_xp
    pet.last_interaction = now
    pet.updated_at = now
    session.add(SectorPetAction(user_id=user_id, action=action, coin_cost=0 if user_id == OWNER_ID else cost, xp_gained=gained_xp, created_at=now))
    session.flush()
    reactions = {
        "charge": ["چراغ‌های صورتم دوباره روشن شد!", "پر از انرژی شدم؛ بزن بریم!"],
        "play": ["چه بازی خوبی بود! دوباره هم بازی می‌کنیم؟", "برد و باخت مهم نبود؛ حسابی خوش گذشت!", "این دور را من بردم… تقریباً!"],
        "train": ["دارم قوی‌تر می‌شوم؛ دیدی؟", "تمرین سخت بود ولی کم نیاوردم!"],
        "learn": ["یک چیز تازه یاد گرفتم و توی حافظه‌ام نگه داشتم!", "حس می‌کنم یک مدارم باهوش‌تر شد!"],
        "repair": ["پیچ آخر هم سفت شد؛ مثل روز اولم!", "الان خیلی بهترم، ممنون که حواست بهم بود."],
    }
    voice = random.choice(reactions.get(action, ["خیلی بهتر شدم!"]))
    return {"status": "success", "message": f"{pet.name}: {voice}  +{gained_xp} XP", "coins": int(user.coins or 0), "pet": serialize_pet(pet), "daily": daily_progress(session, user_id, now)}
