import datetime
import math
import random

from bot.database.models import SectorPet, SectorPetAction, SectorPetGame, SectorPetMemory, SectorPetSocial, User
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

EVOLUTION_PATHS={
    "genius":{"title":"نابغه","icon":"🧠","level":10,"perk":"یادگیری و دانش بیشتر"},
    "warrior":{"title":"جنگجو","icon":"⚔️","level":10,"perk":"قدرت بیشتر در رقابت"},
    "merchant":{"title":"تاجر","icon":"💰","level":10,"perk":"درآمد و پاداش اقتصادی"},
    "shadow":{"title":"سایه","icon":"🕵️","level":10,"perk":"مهارت عملیات مخفی"},
    "companion":{"title":"همراه","icon":"💙","level":10,"perk":"رابطه و شادی بیشتر"},
    "gamer":{"title":"گیمر","icon":"🎮","level":10,"perk":"پاداش بازی بیشتر"},
}
COSMETICS={
    "blue_shell":{"title":"بدنه آبی","icon":"🔵","cost":700,"slot":"body"},
    "gold_shell":{"title":"بدنه طلایی","icon":"🟡","cost":2500,"slot":"body"},
    "captain_hat":{"title":"کلاه فرمانده","icon":"🧢","cost":1200,"slot":"head"},
    "neon_wings":{"title":"بال نئونی","icon":"🪽","cost":3500,"slot":"back"},
    "plasma_tool":{"title":"ابزار پلاسما","icon":"⚔️","cost":2800,"slot":"hand"},
}
JOBS={
    "coder":{"title":"برنامه‌نویس","icon":"💻","hours":4,"reward":140,"xp":25},
    "scientist":{"title":"دانشمند","icon":"🔬","hours":6,"reward":210,"xp":35},
    "astronaut":{"title":"فضانورد","icon":"🚀","hours":8,"reward":320,"xp":45},
    "repairer":{"title":"تعمیرکار","icon":"🔧","hours":3,"reward":100,"xp":18},
}
from bot.services.sector_story import CHAPTERS as NARRATIVE_CHAPTERS

STORY_CHAPTERS={key:{"title":value["title"],"target":len(value["scenes"]),"text":value["scenes"][0]["text"],"region":value["region"],"boss":value["boss"]} for key,value in NARRATIVE_CHAPTERS.items()}


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
        remember(session,user_id,"first_day","اولین دیدار","روزی که سکتور کوچولو برای اولین بار بیدار شد.",5)
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


def care_guidance(pet: SectorPet, coins: int = 0) -> dict:
    """Turn raw stats into one clear next action and a short ordered queue."""
    stats={"energy":int(pet.energy or 0),"happiness":int(pet.happiness or 0),"health":int(pet.health or 0),"hunger":int(pet.hunger or 0),"cleanliness":int(pet.cleanliness or 0)}
    rules=(
        ("health","repair",45,"🔧","یکی از مدارهایم آسیب دیده؛ اول من را تعمیر کن."),
        ("hunger","feed",40,"🍪","گرسنه‌ام و سوختم کم شده؛ به من غذا بده."),
        ("energy","charge",35,"⚡","انرژی‌ام پایین است؛ قبل از بازی یا تمرین شارژم کن."),
        ("cleanliness","clean",40,"🫧","حسگرهایم کثیف شده‌اند؛ وقت تمیزکاری است."),
        ("happiness","play",40,"🎮","دلم گرفته؛ چند دقیقه با من بازی کن."),
    )
    needs=[]
    for stat,action,threshold,icon,message in rules:
        value=stats[stat]
        if value<threshold:
            definition=PET_ACTIONS[action];cost=int(definition["cost"])
            needs.append({"stat":stat,"value":value,"action":action,"title":definition["title"],"icon":icon,"message":message,"cost":cost,"can_afford":int(coins or 0)>=cost,"priority":"critical" if value<20 else "warning"})
    if not needs:
        stat=min(stats,key=stats.get);action={"health":"repair","hunger":"feed","energy":"charge","cleanliness":"clean","happiness":"play"}[stat];definition=PET_ACTIONS[action];cost=int(definition["cost"])
        needs=[{"stat":stat,"value":stats[stat],"action":action,"title":definition["title"],"icon":definition["icon"],"message":"وضعیتم پایدار است. برای ادامه رشد، این کار بهترین انتخاب بعدی است.","cost":cost,"can_afford":int(coins or 0)>=cost,"priority":"normal"}]
    level=level_from_xp(pet.xp);next_level=min(100,level+1);remaining=max(0,xp_for_level(next_level)-int(pet.xp or 0))
    primary=needs[0]
    return {"status":"needs_attention" if primary["priority"]!="normal" else "stable","message":primary["message"],"primary":primary,"needs":needs[:3],"next_level":next_level,"xp_remaining":remaining,"tip":"هر روز ۳ مراقبت و یک بازی انجام بده تا مأموریت روزانه کامل شود."}


def progress_guidance(pet: SectorPet, daily: dict, coins: int = 0, story_used: int = 0, reset_seconds: int = 0) -> dict:
    """Build an ordered, stateful tutorial loop from today's actual progress."""
    base=care_guidance(pet,coins);goals={x["id"]:x for x in daily.get("goals",[])}
    care_done=int(goals.get("care",{}).get("progress",0));needs_done=bool(goals.get("needs",{}).get("complete"));game_done=bool(goals.get("game",{}).get("complete"))
    story_target=int(STORY_CHAPTERS.get(int(pet.story_chapter or 1),{}).get("target",1));story_done=int(pet.story_progress or 0)>=story_target
    steps=[
        {"id":"check","title":"بررسی وضعیت سکتور","detail":"نیاز فوری را برطرف کن","done":needs_done,"tab":"care"},
        {"id":"care","title":"مراقبت روزانه","detail":f"{care_done}/۳ فعالیت انجام شده","done":care_done>=3,"tab":"care"},
        {"id":"game","title":"بازی و دریافت جایزه","detail":"تا ۶۰ سکه + XP","done":game_done,"tab":"games"},
        {"id":"season","title":"بررسی پاداش‌های فصل","detail":"سکه، XP و امتیاز فصل","done":bool(daily.get("complete")),"tab":"season"},
        {"id":"story","title":"هدف داستانی","detail":"مرکز فرمان حرکت واقعی بعدی را مشخص می‌کند","done":story_done,"tab":"command"},
        {"id":"free","title":"هدف آزاد","detail":"رکورد، دارایی یا تعامل","done":False,"tab":"games"},
    ]
    if not needs_done:
        primary=base["primary"];message=f"قدم ۱ از ۴: {base['message']} بعد از انجامش، قدم بعدی را بهت می‌گویم."
    elif care_done<3:
        action="play" if int(pet.happiness or 0)<75 else "learn";definition=PET_ACTIONS[action];primary={"action":action,"title":definition["title"],"icon":definition["icon"],"cost":int(definition["cost"]),"can_afford":int(coins or 0)>=int(definition["cost"]),"priority":"normal","value":care_done*33};message=f"عالی بود! حالا قدم ۲ از ۴: {3-care_done} مراقبت دیگر انجام بده تا مأموریت مراقبت کامل شود."
    elif not game_done:
        primary={"action":"open_games","title":"رفتن به بازی‌ها","icon":"🎮","cost":0,"can_afford":True,"priority":"normal","value":0,"tab":"games"};message="مراقبت امروز کامل شد! حالا قدم ۳ از ۴: یک بازی انجام بده؛ امتیازت مقدار سکه و XP را تعیین می‌کند."
    elif not story_done:
        primary={"action":"open_command","title":"دیدن هدف داستانی","icon":"📖","cost":0,"can_afford":True,"priority":"normal","value":int(pet.story_progress or 0),"tab":"command"};message="برنامه روزانه کامل شد. حالا مرکز فرمان هدف واقعی صحنه بعد را نشان می‌دهد؛ با انجام همان هدف داستان جلو می‌رود."
    else:
        primary={"action":"open_games","title":"ثبت رکورد بهتر","icon":"⭐","cost":0,"can_afford":True,"priority":"normal","value":100,"tab":"games"};message="برنامه محدود امروز کامل شد! حالا رکورد بازی را بهتر کن، دارایی جمع کن یا تعامل اجتماعی انجام بده."
    base.update({"message":message,"primary":primary,"steps":steps,"completed_steps":sum(1 for x in steps if x["done"]),"reset_seconds":int(reset_seconds),"story_daily_used":int(story_used),"story_daily_limit":None,"tip":"داستان سهمیه مصنوعی ندارد؛ هر صحنه با انجام هدف واقعی خودش باز می‌شود."});return base


def serialize_pet(pet: SectorPet, coins: int = 0):
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
        "evolution_path": pet.evolution_path,
        "evolution_path_info": EVOLUTION_PATHS.get(pet.evolution_path),
        "appearance": pet.appearance or {},
        "story_chapter": int(pet.story_chapter or 1), "story_progress": int(pet.story_progress or 0),
        "job": pet.job, "job_started_at": pet.job_started_at.isoformat() if pet.job_started_at else None,
        "notifications_enabled": bool(pet.notifications_enabled),
        "guidance": care_guidance(pet, coins),
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
    personality_points={"play":"بازیگوش","learn":"دانشمند","train":"ماجراجو","repair":"مهربان","feed":"مهربان","sleep":"آرام"}
    if action in personality_points:pet.personality=personality_points[action]
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


def remember(session,user_id:int,kind:str,title:str,detail:str="",importance:int=1):
    row=SectorPetMemory(user_id=user_id,kind=kind,title=title[:120],detail=detail[:500],importance=max(1,min(5,importance)))
    session.add(row);return row


def list_memories(session,user_id:int,limit=30):
    rows=session.query(SectorPetMemory).filter(SectorPetMemory.user_id==user_id).order_by(SectorPetMemory.importance.desc(),SectorPetMemory.created_at.desc()).limit(limit).all()
    return [{"id":r.id,"kind":r.kind,"title":r.title,"detail":r.detail,"importance":r.importance,"created_at":r.created_at.isoformat()} for r in rows]


def pet_achievements(session,pet:SectorPet):
    games=session.query(SectorPetGame).filter(SectorPetGame.user_id==pet.user_id).count();memories=session.query(SectorPetMemory).filter(SectorPetMemory.user_id==pet.user_id).count();social=session.query(SectorPetSocial).filter(SectorPetSocial.actor_id==pet.user_id).count()
    checks=[("first_week","🌱","یک هفته همراهی",int(pet.total_care_days or 0)>=7),("month","🔥","۳۰ روز مراقبت",int(pet.total_care_days or 0)>=30),("gamer","🎮","۲۰ بازی",games>=20),("social","🤝","۱۰ تعامل",social>=10),("memory","📔","۱۰ خاطره",memories>=10),("evolved","🧬","انتخاب مسیر",bool(pet.evolution_path))]
    return [{"id":key,"icon":icon,"title":title} for key,icon,title,ok in checks if ok]


def choose_evolution(session,user_id:int,path_key:str):
    path=EVOLUTION_PATHS.get(path_key);pet=get_or_create_pet(session,user_id,lock=True)
    if not path:return {"status":"error","message":"این مسیر وجود ندارد."}
    if level_from_xp(pet.xp)<path["level"]:return {"status":"error","message":f"انتخاب مسیر از سطح {path['level']} آزاد می‌شود."}
    if pet.evolution_path:return {"status":"error","message":"مسیر تکامل قبلاً انتخاب شده و دائمی است."}
    pet.evolution_path=path_key;pet.xp=int(pet.xp or 0)+100;remember(session,user_id,"evolution",f"انتخاب مسیر {path['title']}",path["perk"],5)
    return {"status":"success","message":f"مسیر {path['icon']} {path['title']} انتخاب شد!","pet":serialize_pet(pet)}


def buy_cosmetic(session,user_id:int,item_key:str):
    item=COSMETICS.get(item_key);user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=get_or_create_pet(session,user_id,lock=True)
    if not item:return {"status":"error","message":"این ظاهر وجود ندارد."}
    inventory=dict(pet.inventory or {});key=f"cosmetic:{item_key}"
    if key not in inventory:
        if user_id!=OWNER_ID and int(user.coins or 0)<item["cost"]:return {"status":"error","message":"سکه کافی نداری."}
        if user_id!=OWNER_ID:user.coins=int(user.coins or 0)-item["cost"]
        inventory[key]=True;pet.inventory=inventory
    appearance=dict(pet.appearance or {});appearance[item["slot"]]=item_key;pet.appearance=appearance
    return {"status":"success","message":f"{item['title']} تجهیز شد.","coins":int(user.coins or 0),"pet":serialize_pet(pet)}


def story_action(session,user_id:int):
    from bot.services import sector_story
    return sector_story.advance(session,user_id)


def job_action(session,user_id:int,job_key=None,now=None):
    now=now or datetime.datetime.utcnow();user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=get_or_create_pet(session,user_id,lock=True)
    if not pet.job:
        job=JOBS.get(job_key)
        if not job:return {"status":"error","message":"یک شغل معتبر انتخاب کن."}
        pet.job=job_key;pet.job_started_at=now;return {"status":"success","message":f"{job['icon']} کار {job['title']} شروع شد.","pet":serialize_pet(pet)}
    job=JOBS[pet.job];started=pet.job_started_at.replace(tzinfo=None) if pet.job_started_at and pet.job_started_at.tzinfo else pet.job_started_at
    if not started or now-started<datetime.timedelta(hours=job["hours"]):
        left=int((datetime.timedelta(hours=job["hours"])-(now-(started or now))).total_seconds())
        return {"status":"error","message":f"هنوز {max(1,left//60)} دقیقه تا پایان کار مانده."}
    reward=job["reward"];user.coins=int(user.coins or 0)+reward;pet.xp=int(pet.xp or 0)+job["xp"];pet.job=None;pet.job_started_at=None
    return {"status":"success","message":f"ماموریت شغلی تمام شد؛ {reward} سکه گرفتی.","coins":int(user.coins or 0),"pet":serialize_pet(pet)}


def social_action(session,actor_id:int,target_id:int,action:str):
    if actor_id==target_id:return {"status":"error","message":"این کار را نمی‌توانی با خودت انجام بدهی."}
    if action not in ("visit","gift","battle"):return {"status":"error","message":"تعامل نامعتبر است."}
    target=session.query(User).filter(User.id==target_id).first();actor=session.query(User).filter(User.id==actor_id).with_for_update().first()
    if not target:return {"status":"error","message":"کاربر مقصد پیدا نشد."}
    day=datetime.datetime.utcnow().strftime("%Y%m%d")
    if session.query(SectorPetSocial.id).filter_by(actor_id=actor_id,target_id=target_id,action=action,day_key=day).first():return {"status":"error","message":"این تعامل امروز قبلاً انجام شده."}
    ap=get_or_create_pet(session,actor_id,lock=True);tp=get_or_create_pet(session,target_id,lock=True);reward=20
    if action=="gift":
        if actor_id!=OWNER_ID and int(actor.coins or 0)<50:return {"status":"error","message":"برای هدیه ۵۰ سکه لازم داری."}
        if actor_id!=OWNER_ID:actor.coins=int(actor.coins or 0)-50
        target.coins=int(target.coins or 0)+50;tp.happiness=min(100,int(tp.happiness or 0)+10)
    elif action=="battle":
        attack=int(ap.level or 1)+int(ap.knowledge or 0)//10+random.randint(1,12);defense=int(tp.level or 1)+int(tp.health or 0)//10+random.randint(1,12);won=attack>=defense
        reward=45 if won else 10;ap.xp=int(ap.xp or 0)+reward;ap.happiness=min(100,int(ap.happiness or 0)+(7 if won else 2))
    else:ap.happiness=min(100,int(ap.happiness or 0)+5);ap.xp=int(ap.xp or 0)+reward
    inventory=dict(ap.inventory or {});inventory["story:social_done"]=datetime.datetime.utcnow().isoformat();ap.inventory=inventory
    session.add(SectorPetSocial(actor_id=actor_id,target_id=target_id,action=action,day_key=day,payload={"reward":reward}))
    message="هدیه فرستاده شد!" if action=="gift" else (("نبرد را بردی!" if won else "این نبرد را باختی؛ اما XP گرفتی.") if action=="battle" else f"به اتاق {tp.name} سر زدی!")
    return {"status":"success","message":message,"coins":int(actor.coins or 0),"pet":serialize_pet(ap)}


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
    if game_key not in ("circuit","battery","pulse","cipher","balance"):return {"status":"error","message":"بازی نامعتبر است."}
    played=session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id,SectorPetGame.game_key==game_key,SectorPetGame.created_at>=start).count()
    if played>=5:return {"status":"error","message":"سهمیه ۵ جایزه امروز این بازی تمام شده."}
    score=max(0,min(100,int(score or 0)));reward=min(60,10+score//2);user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=get_or_create_pet(session,user_id,lock=True)
    if user_id!=OWNER_ID:user.coins=int(user.coins or 0)+reward
    pet.xp=int(pet.xp or 0)+min(30,5+score//5);pet.happiness=min(100,int(pet.happiness or 0)+8)
    session.add(SectorPetGame(user_id=user_id,game_key=game_key,score=score,reward=reward,created_at=now))
    return {"status":"success","message":f"آفرین! {reward} سکه و XP گرفتی.","coins":int(user.coins or 0),"pet":serialize_pet(pet),"daily":daily_progress(session,user_id,now)}
