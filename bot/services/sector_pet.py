import datetime
import math
import random

from bot.database.models import SectorPet, SectorPetAction, SectorPetGame, User
from bot.utils.helpers import OWNER_ID


PET_ACTIONS = {
    "charge": {"title": "شارژ انرژی", "icon": "⚡", "cost": 20, "xp": 10, "energy": 30, "happiness": 3, "knowledge": 0, "health": 3},
    "play": {"title": "بازی", "icon": "🎮", "cost": 15, "xp": 15, "energy": -8, "happiness": 25, "knowledge": 1, "health": 0},
    "train": {"title": "تمرین", "icon": "🏋️", "cost": 30, "xp": 30, "energy": -18, "happiness": 5, "knowledge": 5, "health": 1},
    "learn": {"title": "یادگیری", "icon": "🧠", "cost": 40, "xp": 40, "energy": -12, "happiness": 2, "knowledge": 12, "health": 0},
    "repair": {"title": "تعمیر", "icon": "🔧", "cost": 60, "xp": 15, "energy": 5, "happiness": 4, "knowledge": 0, "health": 35},
    "feed": {"title": "غذا دادن", "icon": "🍪", "cost": 25, "xp": 12, "energy": 8, "happiness": 6, "knowledge": 0, "health": 2, "hunger": 35, "cleanliness": -4},
    "clean": {"title": "تمیزکاری", "icon": "🫧", "cost": 20, "xp": 12, "energy": -2, "happiness": 7, "knowledge": 0, "health": 4, "hunger": 0, "cleanliness": 40},
    "sleep": {"title": "استراحت", "icon": "🌙", "cost": 0, "xp": 8, "energy": 35, "happiness": 3, "knowledge": 0, "health": 5, "hunger": -8, "cleanliness": 0},
}

ROOM_ITEMS = {
    "neon_lamp": {"title": "چراغ نئونی", "icon": "💡", "cost": 450, "level": 2},
    "game_console": {"title": "کنسول بازی", "icon": "🕹️", "cost": 900, "level": 5},
    "space_window": {"title": "پنجره فضایی", "icon": "🪐", "cost": 1800, "level": 10},
    "ai_core": {"title": "هسته هوشمند", "icon": "🔮", "cost": 4000, "level": 20},
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
        pet.hunger = max(0, int(pet.hunger if pet.hunger is not None else 80) - min(45, hours * 2))
        pet.cleanliness = max(0, int(pet.cleanliness if pet.cleanliness is not None else 80) - min(35, hours))
        if pet.energy == 0 or pet.happiness == 0 or pet.hunger == 0 or pet.cleanliness == 0:
            pet.health = max(20, int(pet.health or 100) - min(20, hours))
        pet.last_interaction = now
        pet.updated_at = now


def daily_progress(session, user_id: int, now=None):
    now = now or datetime.datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    actions = session.query(SectorPetAction).filter(SectorPetAction.user_id == user_id, SectorPetAction.created_at >= start).all()
    games = session.query(SectorPetGame).filter(SectorPetGame.user_id == user_id, SectorPetGame.created_at >= start).count()
    kinds = {row.action for row in actions}
    goals = [
        {"id":"care","title":"۳ مراقبت انجام بده","progress":min(len(actions),3),"target":3,"complete":len(actions)>=3},
        {"id":"needs","title":"غذا یا نظافت","progress":1 if kinds.intersection({"feed","clean"}) else 0,"target":1,"complete":bool(kinds.intersection({"feed","clean"}))},
        {"id":"game","title":"یک بازی سکتوری","progress":min(games,1),"target":1,"complete":games>=1},
    ]
    done=sum(1 for goal in goals if goal["complete"])
    return {"actions": len(actions), "target": 3, "complete": done == len(goals), "goals":goals, "completed_goals":done, "full_xp_remaining": max(0, 5 - len(actions))}


def pet_mood(pet: SectorPet) -> dict:
    stats={"energy":int(pet.energy or 0),"happiness":int(pet.happiness or 0),"health":int(pet.health or 0),"hunger":int(pet.hunger or 0),"cleanliness":int(pet.cleanliness or 0)}
    if pet.sleeping:return {"id":"sleeping","title":"خواب‌آلود","emoji":"😴","line":"هیس… مدارهایم در حال شارژند."}
    key=min(stats,key=stats.get)
    if stats[key]<25:
        return {"id":key,"title":{"energy":"خسته","happiness":"دلگیر","health":"خراب","hunger":"گرسنه","cleanliness":"کثیف"}[key],"emoji":{"energy":"🥱","happiness":"🥺","health":"🤕","hunger":"😋","cleanliness":"🫠"}[key],"line":{"energy":"یک استراحت حسابی لازم دارم.","happiness":"بیا کمی با هم بازی کنیم.","health":"چند تا پیچم شل شده!","hunger":"باتری‌کوکی داری؟","cleanliness":"وقت برق انداختن بدنه‌ام رسیده."}[key]}
    if int(pet.happiness or 0)>=80:return {"id":"happy","title":"سرحال","emoji":"🤩","line":"امروز برای یک ماجراجویی آماده‌ام!"}
    return {"id":"calm","title":"آرام","emoji":"🤖","line":"خوشحالم که برگشتی؛ امروز چه کار کنیم؟"}


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
        "hunger": int(pet.hunger if pet.hunger is not None else 80), "cleanliness": int(pet.cleanliness if pet.cleanliness is not None else 80),
        "personality": pet.personality or "کنجکاو", "room_level": int(pet.room_level or 1),
        "inventory": pet.inventory or {}, "equipped_item": pet.equipped_item, "sleeping": bool(pet.sleeping),
        "mood": pet_mood(pet),
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
    for field in ("energy", "happiness", "knowledge", "health", "hunger", "cleanliness"):
        delta=int(definition.get(field,0));current=getattr(pet,field)
        setattr(pet, field, max(0, min(100, int(current if current is not None else 80) + delta)))
    pet.sleeping = action == "sleep"
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
        "feed": ["هوم! باتری‌کوکی خیلی خوشمزه بود!", "حالا برای ماجراجویی سوخت دارم!"],
        "clean": ["نگاه کن چقدر برق می‌زنم!", "حتی آنتنم هم تمیز شد!"],
        "sleep": ["چشم‌هایم را چند دقیقه خاموش می‌کنم…", "حالت ذخیره انرژی فعال شد؛ شب بخیر!"],
    }
    voice = random.choice(reactions.get(action, ["خیلی بهتر شدم!"]))
    return {"status": "success", "message": f"{pet.name}: {voice}  +{gained_xp} XP", "coins": int(user.coins or 0), "pet": serialize_pet(pet), "daily": daily_progress(session, user_id, now)}


def buy_room_item(session,user_id:int,item_key:str):
    item=ROOM_ITEMS.get(item_key)
    if not item:return {"status":"error","message":"این وسیله پیدا نشد."}
    user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=get_or_create_pet(session,user_id,lock=True)
    inventory=dict(pet.inventory or {})
    if item_key in inventory:return {"status":"error","message":"این وسیله را قبلاً خریده‌ای."}
    if pet.level<item["level"]:return {"status":"error","message":f"این وسیله از سطح {item['level']} آزاد می‌شود."}
    if user_id!=OWNER_ID and int(user.coins or 0)<item["cost"]:return {"status":"error","message":"سکه کافی نداری."}
    if user_id!=OWNER_ID:user.coins=int(user.coins or 0)-item["cost"]
    inventory[item_key]=True;pet.inventory=inventory;pet.equipped_item=item_key;pet.happiness=min(100,int(pet.happiness or 0)+10);pet.xp=int(pet.xp or 0)+25
    return {"status":"success","message":f"{item['title']} به اتاق اضافه شد!","coins":int(user.coins or 0),"pet":serialize_pet(pet)}


def finish_minigame(session,user_id:int,game_key:str,score:int,now=None):
    now=now or datetime.datetime.utcnow();start=now.replace(hour=0,minute=0,second=0,microsecond=0)
    if game_key not in ("circuit","battery"):return {"status":"error","message":"بازی نامعتبر است."}
    played=session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id,SectorPetGame.game_key==game_key,SectorPetGame.created_at>=start).count()
    if played>=5:return {"status":"error","message":"سهمیه ۵ جایزه امروز این بازی تمام شده."}
    score=max(0,min(100,int(score or 0)));reward=min(60,10+score//2);user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=get_or_create_pet(session,user_id,lock=True)
    if user_id!=OWNER_ID:user.coins=int(user.coins or 0)+reward
    pet.xp=int(pet.xp or 0)+min(30,5+score//5);pet.happiness=min(100,int(pet.happiness or 0)+8)
    session.add(SectorPetGame(user_id=user_id,game_key=game_key,score=score,reward=reward,created_at=now))
    return {"status":"success","message":f"آفرین! {reward} سکه و XP گرفتی.","coins":int(user.coins or 0),"pet":serialize_pet(pet),"daily":daily_progress(session,user_id,now)}
