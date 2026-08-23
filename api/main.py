from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import json
import os
import time
import datetime
import secrets
import random
import ast
import operator
import httpx
from typing import Optional
from urllib.parse import unquote
from sqlalchemy import func

from bot.database.session import get_session
from bot.database.models import User, Group, Purchase, AppSetting, Order, Referral, GameSession, GameScore, SectorPet, SectorPetAction
from api.quiz_bank import QUIZ_BANK
from bot.modules.ai import get_ai_response, get_sector_prompt, load_ai_history, save_ai_turn, needs_web_search

app = FastAPI(title="iSectorLand Unified API", version="3.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

BOT_TOKEN = os.getenv("BOT_TOKEN", "")


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


OWNER_ID = _env_int("OWNER_ID", 5147526780)


MAX_INIT_DATA_AGE = _env_int("TELEGRAM_INIT_DATA_MAX_AGE", 3600)

SHOP_ITEMS = {
    1: {"name": "VPN یک ماهه", "price": 15000, "kind":"vpn", "days":30, "volume":"۵۰ گیگابایت", "devices":2, "region":"اروپا", "warranty":"تعویض در صورت قطعی"},
    2: {"name": "VPN سه ماهه", "price": 40000, "kind":"vpn", "days":90, "volume":"۱۵۰ گیگابایت", "devices":3, "region":"اروپا", "warranty":"پشتیبانی کامل"},
    3: {"name": "پک استیکر اختصاصی", "price": 8000},
    4: {"name": "لقب سفارشی در گروه", "price": 25000},
    5: {"name": "VPN شش ماهه", "price": 75000, "kind":"vpn", "days":180, "volume":"۳۰۰ گیگابایت", "devices":5, "region":"اروپا", "warranty":"پشتیبانی VIP"},
    6: {"name": "عضویت VIP یک ماهه", "price": 30000, "kind":"vip", "days":30, "benefits":["گردونه هر ۱۲ ساعت","شانس بیشتر جوایز ویژه","هدیه روزانه بیشتر"]},
}

WHEEL_PRIZES = [
    {"kind":"coins","label":"۲۵ سکه","coins":25},
    {"kind":"coins","label":"۵۰ سکه","coins":50},
    {"kind":"coins","label":"۱۰۰ سکه","coins":100},
    {"kind":"coins","label":"۲۰۰ سکه","coins":200},
    {"kind":"coins","label":"۳۰۰ سکه","coins":300},
    {"kind":"config","label":"کانفیگ رایگان","coins":0},
    {"kind":"proxy","label":"پروکسی تلگرام","coins":0},
    {"kind":"coins","label":"۷۵ سکه","coins":75},
]

QUIZ_BY_ID = {q["id"]: q for q in QUIZ_BANK}

SETTING_DEFAULTS = {
    "maintenance_mode": False,
    "vpn_price_1m": 15000,
    "vpn_price_3m": 40000,
    "vpn_price_6m": 75000,
    "vip_price_1m": 30000,
    "daily_reward": 50,
    "vip_daily_reward": 75,
    "wheel_cooldown_hours": 24,
    "referral_reward": 250,
    "weekly_tournament_enabled": False,
    "coupon_codes": {"SECTOR10":10,"VIP15":15},
    "config_inventory": [],
    "proxy_inventory": [],
    "wheel_weights": {"0":24,"1":20,"2":14,"3":8,"4":4,"5":2,"6":3,"7":16},
}
ADMIN_SETTING_KEYS = set(SETTING_DEFAULTS)
WEATHER_LABELS = {0:"صاف",1:"عمدتاً صاف",2:"نیمه‌ابری",3:"ابری",45:"مه‌آلود",48:"مه یخ‌زن",51:"نم‌نم باران",53:"باران ریز",55:"باران شدید",61:"باران",63:"باران متوسط",65:"باران شدید",71:"برف",73:"برف متوسط",75:"برف شدید",80:"رگبار",81:"رگبار متوسط",82:"رگبار شدید",95:"رعدوبرق"}
MISSION_DEFS = {
    "daily_quiz_3":{"title":"سه پاسخ مسابقه","target":3,"coins":60,"xp":25,"period":"daily","kind":"quiz"},
    "daily_tools_2":{"title":"دو بار استفاده از دستیار","target":2,"coins":35,"xp":15,"period":"daily","kind":"tools"},
    "daily_wheel":{"title":"چرخاندن گردونه","target":1,"coins":25,"xp":10,"period":"daily","kind":"wheel"},
    "weekly_quiz_15":{"title":"۱۵ پاسخ مسابقه","target":15,"coins":250,"xp":100,"period":"weekly","kind":"quiz"},
    "weekly_tools_5":{"title":"پنج بار استفاده از دستیار","target":5,"coins":100,"xp":40,"period":"weekly","kind":"tools"},
    "daily_sector_3":{"title":"سه بار مراقبت از سکتور","target":3,"coins":80,"xp":35,"period":"daily","kind":"sector"},
}
GAME_LIMITS={
    "racer":{"max_score":2_000_000,"min_seconds":8},"galaxy":{"max_score":5_000_000,"min_seconds":8},
    "snake3d":{"max_score":1_000_000,"min_seconds":5},"2048":{"max_score":1_000_000,"min_seconds":10},
    "tetris":{"max_score":2_000_000,"min_seconds":10},"memory":{"max_score":100_000,"min_seconds":4},
    "mines":{"max_score":100_000,"min_seconds":4},"airforce":{"max_score":5_000_000,"min_seconds":8},
    "blockblast":{"max_score":2_000_000,"min_seconds":8},
}


def load_settings(session) -> dict:
    result = dict(SETTING_DEFAULTS)
    for row in session.query(AppSetting).filter(AppSetting.key.in_(ADMIN_SETTING_KEYS)).all():
        result[row.key] = row.value
    return result


def effective_shop_items(session) -> dict:
    settings = load_settings(session)
    items = {key: dict(value) for key, value in SHOP_ITEMS.items()}
    items[1]["price"] = int(settings["vpn_price_1m"])
    items[2]["price"] = int(settings["vpn_price_3m"])
    items[5]["price"] = int(settings["vpn_price_6m"])
    items[6]["price"] = int(settings["vip_price_1m"])
    return items


def serialize_order(order:Order):
    return {"id":order.id,"item_key":order.item_key,"name":order.item_name,"price":int(order.price or 0),"status":order.status,"created_at":order.created_at.isoformat() if order.created_at else None,"expires_at":order.expires_at.isoformat() if order.expires_at else None,"metadata":order.metadata_json or {}}


def is_platform_admin(session, user_id: int) -> bool:
    if int(user_id) == OWNER_ID:
        return True
    user = session.query(User).filter(User.id == int(user_id)).first()
    return bool(user and user.is_admin)


def require_admin(init_data: Optional[str]) -> tuple[dict, object]:
    telegram_user = require_user(init_data)
    session = get_session()
    if not is_platform_admin(session, int(telegram_user["id"])):
        session.close()
        raise HTTPException(status_code=403, detail="Admin access required")
    return telegram_user, session


def safe_calculate(expression: str) -> float:
    if not expression or len(expression) > 100:
        raise ValueError("invalid expression")
    operations = {ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod,ast.Pow:operator.pow,ast.USub:operator.neg,ast.UAdd:operator.pos}
    def evaluate(node):
        if isinstance(node,ast.Expression): return evaluate(node.body)
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)) and not isinstance(node.value,bool): return node.value
        if isinstance(node,ast.BinOp) and type(node.op) in operations:
            left,right=evaluate(node.left),evaluate(node.right)
            if isinstance(node.op,ast.Pow) and abs(right)>8: raise ValueError("power too large")
            value=operations[type(node.op)](left,right)
            if abs(value)>1e15: raise ValueError("result too large")
            return value
        if isinstance(node,ast.UnaryOp) and type(node.op) in operations: return operations[type(node.op)](evaluate(node.operand))
        raise ValueError("unsupported expression")
    return evaluate(ast.parse(expression,mode="eval"))


def mission_window(period: str):
    now=datetime.datetime.utcnow()
    if period=="daily": start=now.replace(hour=0,minute=0,second=0,microsecond=0); key=start.strftime("%Y%m%d")
    else: start=(now-datetime.timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0); key=start.strftime("%Y%m%d")
    return start,key


def mission_progress(session,user_id:int,definition:dict,start:datetime.datetime)->int:
    query=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.created_at>=start)
    if definition["kind"]=="quiz": return query.filter(Purchase.status.in_(("quiz_correct","quiz_wrong"))).count()
    if definition["kind"]=="tools": return query.filter(Purchase.item_id=="miniapp_ai").count()
    if definition["kind"]=="wheel": return query.filter(Purchase.item_id.like("wheel_%")).count()
    if definition["kind"]=="sector": return session.query(SectorPetAction).filter(SectorPetAction.user_id==user_id,SectorPetAction.created_at>=start).count()
    return 0


PET_ACTIONS={
    "charge":{"title":"شارژ انرژی","cost":20,"xp":10,"energy":30,"happiness":3,"knowledge":0,"health":3},
    "play":{"title":"بازی","cost":15,"xp":15,"energy":-8,"happiness":25,"knowledge":1,"health":0},
    "train":{"title":"تمرین","cost":30,"xp":30,"energy":-18,"happiness":5,"knowledge":5,"health":1},
    "learn":{"title":"یادگیری","cost":40,"xp":40,"energy":-12,"happiness":2,"knowledge":12,"health":0},
    "repair":{"title":"تعمیر","cost":60,"xp":15,"energy":5,"happiness":4,"knowledge":0,"health":35},
}


def pet_stage(level:int)->dict:
    if level>=25:return {"id":4,"title":"سکتور همه‌چیزدان","next_level":None}
    if level>=12:return {"id":3,"title":"سکتور حرفه‌ای","next_level":25}
    if level>=5:return {"id":2,"title":"سکتور کنجکاو","next_level":12}
    return {"id":1,"title":"سکتور کوچولو","next_level":5}


def refresh_pet(pet:SectorPet,now:datetime.datetime):
    last=pet.last_interaction.replace(tzinfo=None) if pet.last_interaction and pet.last_interaction.tzinfo else pet.last_interaction
    hours=max(0,int((now-(last or now)).total_seconds()//3600))
    if hours:
        pet.energy=max(0,int(pet.energy or 0)-min(40,hours*2));pet.happiness=max(0,int(pet.happiness or 0)-min(30,hours))
        if pet.energy==0 or pet.happiness==0:pet.health=max(20,int(pet.health or 100)-min(20,hours))
        pet.last_interaction=now;pet.updated_at=now


def serialize_pet(pet:SectorPet):
    level=max(1,min(100,1+int(pet.xp or 0)//250));pet.level=level
    return {"name":pet.name,"level":level,"xp":int(pet.xp or 0),"xp_in_level":int(pet.xp or 0)%250,"xp_next":250,"energy":int(pet.energy or 0),"happiness":int(pet.happiness or 0),"knowledge":int(pet.knowledge or 0),"health":int(pet.health or 0),"stage":pet_stage(level)}


def user_achievements(session,user:User)->list:
    correct=session.query(Purchase).filter(Purchase.user_id==user.id,Purchase.status=="quiz_correct").count()
    wheel=session.query(Purchase).filter(Purchase.user_id==user.id,Purchase.item_id.like("wheel_%")).count()
    items=[]
    if correct>=1: items.append({"id":"first_answer","icon":"🎯","title":"اولین پاسخ درست"})
    if correct>=10: items.append({"id":"quiz_10","icon":"🧠","title":"ذهن برتر"})
    if correct>=50: items.append({"id":"quiz_50","icon":"🏆","title":"استاد مسابقه"})
    if wheel>=5: items.append({"id":"wheel_5","icon":"🎡","title":"خوش‌شانس"})
    if int(user.level or 1)>=5: items.append({"id":"level_5","icon":"⭐","title":"سطح پنج"})
    if int(user.coins or 0)>=5000: items.append({"id":"wealth_5k","icon":"💰","title":"سرمایه‌دار"})
    joined=user.joined_at.replace(tzinfo=None) if user.joined_at and user.joined_at.tzinfo else user.joined_at
    if joined and datetime.datetime.utcnow()-joined>=datetime.timedelta(days=30): items.append({"id":"veteran","icon":"🛡️","title":"عضو قدیمی"})
    return items


@app.post("/api/tools/assistant/{user_id}")
async def miniapp_assistant(user_id:int, request:dict, init_data:Optional[str]=Header(None,alias="init-data")):
    telegram_user=require_user(init_data,user_id)
    message=str(request.get("message") or "").strip()
    mode=str(request.get("mode") or "chat")
    if not message or len(message)>1500: raise HTTPException(status_code=400,detail="پیام نامعتبر است.")
    session=get_session()
    try:
        since=datetime.datetime.utcnow()-datetime.timedelta(hours=1)
        used=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.item_id=="miniapp_ai",Purchase.created_at>=since).count()
        if used>=30 and user_id!=OWNER_ID: raise HTTPException(status_code=429,detail="سقف استفاده ساعتی دستیار پر شده است.")
        history=load_ai_history(user_id,24)
        prompt=get_sector_prompt(type("MiniUser",(),{"id":user_id,"first_name":telegram_user.get("first_name") or "کاربر"})())
        if mode=="translate": prompt="متن را اگر فارسی است به انگلیسی و اگر غیرفارسی است به فارسی ترجمه کن. فقط ترجمه را برگردان."
        response=await get_ai_response(prompt,message,use_search=needs_web_search(message),history=history)
        if not response: raise HTTPException(status_code=503,detail="دستیار موقتاً در دسترس نیست.")
        save_ai_turn(user_id,user_id,message,response)
        session.add(Purchase(user_id=user_id,item_id="miniapp_ai",amount=0,status="activity"));session.commit()
        return {"response":response[:4000],"remaining":max(0,29-used)}
    finally: session.close()


@app.get("/api/tools/weather")
async def miniapp_weather(city:str, init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data)
    city=city.strip()[:80]
    if len(city)<2: raise HTTPException(status_code=400,detail="نام شهر را وارد کن.")
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            geo=await client.get("https://geocoding-api.open-meteo.com/v1/search",params={"name":city,"count":1,"language":"fa","format":"json"})
            geo.raise_for_status(); places=geo.json().get("results") or []
            if not places: raise HTTPException(status_code=404,detail="شهر پیدا نشد.")
            place=places[0]
            weather=await client.get("https://api.open-meteo.com/v1/forecast",params={"latitude":place["latitude"],"longitude":place["longitude"],"current":"temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m","timezone":"auto"})
            weather.raise_for_status(); current=weather.json().get("current") or {}
            return {"city":place.get("name") or city,"country":place.get("country") or "","temperature":current.get("temperature_2m"),"feels_like":current.get("apparent_temperature"),"humidity":current.get("relative_humidity_2m"),"wind":current.get("wind_speed_10m"),"condition":WEATHER_LABELS.get(int(current.get("weather_code",-1)),"نامشخص")}
    except HTTPException: raise
    except Exception: raise HTTPException(status_code=502,detail="سرویس هواشناسی پاسخ نداد.")


@app.post("/api/tools/calculate")
async def miniapp_calculate(request:dict, init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data)
    try: result=safe_calculate(str(request.get("expression") or ""))
    except Exception: raise HTTPException(status_code=400,detail="عبارت ریاضی معتبر نیست.")
    return {"result":round(float(result),10)}


@app.get("/api/missions/{user_id}")
async def get_missions(user_id:int, init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id);session=get_session()
    try:
        result=[]
        for mission_id,definition in MISSION_DEFS.items():
            start,period_key=mission_window(definition["period"]);progress=mission_progress(session,user_id,definition,start)
            claim_key=f"mission:{user_id}:{mission_id}:{period_key}"
            claimed=session.query(Purchase.id).filter(Purchase.telegram_payment_charge_id==claim_key).first() is not None
            result.append({"id":mission_id,**definition,"progress":min(progress,definition["target"]),"complete":progress>=definition["target"],"claimed":claimed})
        return result
    finally:session.close()


@app.post("/api/missions/{user_id}/{mission_id}/claim")
async def claim_mission(user_id:int,mission_id:str,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id);definition=MISSION_DEFS.get(mission_id)
    if not definition:raise HTTPException(status_code=404,detail="مأموریت پیدا نشد.")
    session=get_session()
    try:
        user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not user:raise HTTPException(status_code=404,detail="User not found")
        start,period_key=mission_window(definition["period"]);claim_key=f"mission:{user_id}:{mission_id}:{period_key}"
        if session.query(Purchase.id).filter(Purchase.telegram_payment_charge_id==claim_key).first():return {"status":"error","message":"جایزه این مأموریت قبلاً دریافت شده."}
        if mission_progress(session,user_id,definition,start)<definition["target"]:return {"status":"error","message":"مأموریت هنوز کامل نشده."}
        user.coins=int(user.coins or 0)+definition["coins"];user.xp=int(user.xp or 0)+definition["xp"];user.level=level_for_xp(user.xp)
        session.add(Purchase(user_id=user_id,item_id="mission_reward",amount=definition["coins"],status="reward",telegram_payment_charge_id=claim_key));session.commit()
        return {"status":"success","coins":user.coins,"xp":user.xp,"level":user.level,"reward":{"coins":definition["coins"],"xp":definition["xp"]}}
    finally:session.close()


def validate_telegram_init_data(init_data: Optional[str]) -> dict:
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")
    try:
        pairs, values, received_hash = [], {}, None
        for part in init_data.split("&"):
            if "=" not in part:
                continue
            key, raw_value = part.split("=", 1)
            value = unquote(raw_value)
            if key == "hash": received_hash = value
            else:
                values[key] = value
                pairs.append(f"{key}={value}")
        if not received_hash:
            raise HTTPException(status_code=401, detail="Telegram hash missing")
        pairs.sort()
        data_check_string = "\n".join(pairs)
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated, received_hash):
            raise HTTPException(status_code=403, detail="Invalid Telegram signature")
        auth_date = int(values.get("auth_date", "0"))
        now = int(time.time())
        if not auth_date or abs(now - auth_date) > MAX_INIT_DATA_AGE:
            raise HTTPException(status_code=403, detail="Expired Telegram init data")
        user = json.loads(values.get("user", "{}"))
        if not user.get("id"):
            raise HTTPException(status_code=403, detail="Telegram user missing")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid Telegram init data")


def require_user(init_data: Optional[str], requested_user_id: Optional[int] = None) -> dict:
    user = validate_telegram_init_data(init_data)
    if requested_user_id is not None and int(user["id"]) != int(requested_user_id):
        raise HTTPException(status_code=403, detail="User mismatch")
    return user


def level_for_xp(xp: int) -> int:
    return max(1, int(xp or 0) // 100 + 1)


def serialize_purchase(p: Purchase):
    item = SHOP_ITEMS.get(int(p.item_id)) if str(p.item_id).isdigit() else None
    return {"id":p.id,"item_id":p.item_id,"name":item["name"] if item else p.item_id,"amount":int(p.amount or 0),"status":p.status,"created_at":p.created_at.isoformat() if p.created_at else None}


@app.get("/api/user/{user_id}")
async def get_user(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user: raise HTTPException(status_code=404, detail="User not found")
        rank = session.query(User).filter(User.coins > user.coins).count() + 1
        orders_count = session.query(Purchase).filter(Purchase.user_id == user_id).count()
        total_spent = session.query(func.coalesce(func.sum(Purchase.amount), 0)).filter(Purchase.user_id == user_id, Purchase.status == "coin_purchase").scalar() or 0
        correct_answers=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.status=="quiz_correct").count()
        return {"id":user.id,"first_name":"فرمانده پیمان" if user.id==OWNER_ID else user.first_name,"username":user.username,"coins":int(user.coins or 0),"unlimited_wallet":user.id==OWNER_ID,"role":"فرمانده و مسئول اصلی SectorLand" if user.id==OWNER_ID else "کاربر","bank_balance":int(user.bank_balance or 0),"loan_balance":int(user.loan_balance or 0),"xp":int(user.xp or 0),"level":int(user.level or 1),"rank":rank,"joined_at":user.joined_at.isoformat() if user.joined_at else None,"achievements":user_achievements(session,user),"correct_answers":correct_answers,"message_count":int(user.message_count or 0),"orders_count":orders_count,"total_spent":int(total_spent),"referrals":0,"is_admin":is_platform_admin(session,user.id),"vip_until":user.vip_until.isoformat() if user.vip_until else None}
    finally: session.close()


@app.get("/api/sector-pet/{user_id}")
async def get_sector_pet(user_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id);session=get_session()
    try:
        now=datetime.datetime.utcnow();pet=session.query(SectorPet).filter(SectorPet.user_id==user_id).first()
        if not pet:pet=SectorPet(user_id=user_id,last_interaction=now,created_at=now,updated_at=now);session.add(pet);session.flush()
        refresh_pet(pet,now);data=serialize_pet(pet);session.commit();return {"pet":data,"actions":[{"id":key,**value} for key,value in PET_ACTIONS.items()]}
    finally:session.close()


@app.post("/api/sector-pet/{user_id}/{action}")
async def sector_pet_action(user_id:int,action:str,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id);definition=PET_ACTIONS.get(action)
    if not definition:raise HTTPException(status_code=404,detail="Action not found")
    session=get_session()
    try:
        now=datetime.datetime.utcnow();user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not user:raise HTTPException(status_code=404,detail="User not found")
        recent=session.query(SectorPetAction).filter(SectorPetAction.user_id==user_id,SectorPetAction.created_at>=now-datetime.timedelta(minutes=1)).count()
        if recent>=8:raise HTTPException(status_code=429,detail="سکتور کمی استراحت می‌خواهد؛ یک دقیقه بعد برگرد.")
        pet=session.query(SectorPet).filter(SectorPet.user_id==user_id).with_for_update().first()
        if not pet:pet=SectorPet(user_id=user_id,last_interaction=now,created_at=now,updated_at=now);session.add(pet);session.flush()
        refresh_pet(pet,now);cost=int(definition["cost"])
        if user.id!=OWNER_ID and int(user.coins or 0)<cost:return {"status":"error","message":"برای این کار سکه کافی نداری."}
        if user.id!=OWNER_ID:user.coins=int(user.coins or 0)-cost
        for field in ("energy","happiness","knowledge","health"):
            setattr(pet,field,max(0,min(100,int(getattr(pet,field) or 0)+int(definition[field]))))
        pet.xp=int(pet.xp or 0)+int(definition["xp"]);pet.last_interaction=now;pet.updated_at=now
        session.add(SectorPetAction(user_id=user_id,action=action,coin_cost=0 if user.id==OWNER_ID else cost,xp_gained=definition["xp"],created_at=now));session.commit()
        return {"status":"success","message":f"{definition['title']} انجام شد؛ سکتور +{definition['xp']} XP گرفت!","coins":int(user.coins or 0),"pet":serialize_pet(pet)}
    except:
        session.rollback();raise
    finally:session.close()


@app.post("/api/daily-claim/{user_id}")
async def claim_daily(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404, detail="User not found")
        now = datetime.datetime.utcnow()
        last = user.last_daily_claim.replace(tzinfo=None) if user.last_daily_claim and user.last_daily_claim.tzinfo else user.last_daily_claim
        if last and now-last < datetime.timedelta(hours=24):
            remaining = datetime.timedelta(hours=24)-(now-last)
            return {"status":"error","message":"هنوز ۲۴ ساعت کامل نشده.","remaining_seconds":int(remaining.total_seconds())}
        vip_until = user.vip_until.replace(tzinfo=None) if user.vip_until and user.vip_until.tzinfo else user.vip_until
        settings = load_settings(session)
        reward = int(settings["vip_daily_reward"] if vip_until and vip_until>now else settings["daily_reward"])
        user.coins = int(user.coins or 0)+reward
        user.last_daily_claim = now
        session.add(Purchase(user_id=user.id,item_id="daily_reward",amount=reward,status="reward"))
        session.commit()
        return {"status":"success","reward":reward,"coins":user.coins}
    finally: session.close()


@app.post("/api/wheel/spin/{user_id}")
async def spin_wheel(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        now = datetime.datetime.utcnow()
        last = session.query(Purchase).filter(
            Purchase.user_id == user_id,
            Purchase.item_id.like("wheel_%"),
        ).order_by(Purchase.created_at.desc()).first()
        last_time = last.created_at.replace(tzinfo=None) if last and last.created_at and last.created_at.tzinfo else (last.created_at if last else None)
        settings=load_settings(session)
        vip_until = user.vip_until.replace(tzinfo=None) if user.vip_until and user.vip_until.tzinfo else user.vip_until
        is_vip=bool(vip_until and vip_until>now)
        cooldown_hours = max(1, min(168, int(settings["wheel_cooldown_hours"])))
        if is_vip: cooldown_hours=max(1,cooldown_hours//2)
        if last_time and now - last_time < datetime.timedelta(hours=cooldown_hours):
            remaining = datetime.timedelta(hours=cooldown_hours) - (now - last_time)
            return {"status":"error","message":"گردونه امروز را چرخاندی.","remaining_seconds":int(remaining.total_seconds())}

        configured_weights=settings.get("wheel_weights") or {}
        weights=[max(0,int(configured_weights.get(str(i),1))) for i in range(len(WHEEL_PRIZES))]
        if is_vip:
            weights=[round(weight*1.6) if WHEEL_PRIZES[i]["kind"] in ("config","proxy") or int(WHEEL_PRIZES[i].get("coins",0))>=200 else weight for i,weight in enumerate(weights)]
        total=sum(weights)
        if total<=0: weights=[1]*len(WHEEL_PRIZES);total=len(WHEEL_PRIZES)
        pick=secrets.randbelow(total);prize_index=0
        for i,weight in enumerate(weights):
            if pick<weight: prize_index=i;break
            pick-=weight
        prize = WHEEL_PRIZES[prize_index]
        coins = int(prize.get("coins", 0))
        message = "جایزه به حسابت اضافه شد."
        delivery = None
        if prize["kind"] in ("config", "proxy"):
            inventory_key = "config_inventory" if prize["kind"] == "config" else "proxy_inventory"
            inventory_row = session.query(AppSetting).filter(AppSetting.key == inventory_key).with_for_update().first()
            inventory = list(inventory_row.value or []) if inventory_row else []
            if inventory:
                delivery = str(inventory.pop(0)).strip()
                if inventory_row:
                    inventory_row.value = inventory
                    inventory_row.updated_at = now
                else:
                    session.add(AppSetting(key=inventory_key, value=inventory, updated_at=now))
                session.add(Order(
                    user_id=user.id,
                    item_key="wheel_" + prize["kind"],
                    item_name=prize["label"],
                    price=0,
                    status="delivered",
                    metadata_json={"delivery": delivery, "source": "wheel"},
                ))
                message = "جایزه آماده شد و در سفارش‌های من قرار گرفت."
            else:
                coins = 150
                prize = {"kind":"coins","label":"۱۵۰ سکه جایگزین","coins":coins}
                message = "موجودی جایزه ویژه تمام شده بود؛ ۱۵۰ سکه جایگزین دریافت کردی."
        if coins:
            user.coins = int(user.coins or 0) + coins
        session.add(Purchase(
            user_id=user.id,
            item_id="wheel_" + prize["kind"],
            amount=coins,
            status="reward",
        ))
        session.commit()
        return {"status":"success","index":prize_index,"prize":prize,"coins":int(user.coins or 0),"message":message}
    finally:
        session.close()


@app.get("/api/wheel/history/{user_id}")
async def wheel_history(user_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id);session=get_session()
    try:
        rows=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.item_id.like("wheel_%")).order_by(Purchase.created_at.desc()).limit(10).all()
        labels={"wheel_coins":"جایزه سکه","wheel_config":"کانفیگ رایگان","wheel_proxy":"پروکسی تلگرام"}
        return [{"id":p.id,"label":labels.get(str(p.item_id),"جایزه گردونه"),"coins":int(p.amount or 0),"created_at":p.created_at.isoformat() if p.created_at else None} for p in rows]
    finally:session.close()


@app.get("/api/bank/{user_id}")
async def get_bank(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session=get_session()
    try:
        user=session.query(User).filter(User.id==user_id).first()
        if not user: raise HTTPException(status_code=404,detail="User not found")
        return {"coins":int(user.coins or 0),"bank_balance":int(user.bank_balance or 0),"loan_balance":int(user.loan_balance or 0)}
    finally: session.close()


@app.post("/api/bank/{user_id}/{action}")
async def bank_action(user_id:int, action:str, amount:int=0, init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id)
    if amount < 0: raise HTTPException(status_code=400,detail="Invalid amount")
    session=get_session()
    try:
        user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404,detail="User not found")
        coins, bank, loan = int(user.coins or 0), int(user.bank_balance or 0), int(user.loan_balance or 0)
        if action=="deposit":
            if amount<=0 or coins<amount: return {"status":"error","message":"سکه کافی برای واریز نداری."}
            user.coins=coins-amount; user.bank_balance=bank+amount; label="bank_deposit"
        elif action=="withdraw":
            if amount<=0 or bank<amount: return {"status":"error","message":"موجودی بانک کافی نیست."}
            user.bank_balance=bank-amount; user.coins=coins+amount; label="bank_withdraw"
        elif action=="loan":
            if loan>0: return {"status":"error","message":"اول وام قبلی رو تسویه کن."}
            if amount<=0 or amount>5000: return {"status":"error","message":"مبلغ وام باید بین ۱ تا ۵۰۰۰ سکه باشد."}
            user.loan_balance=amount; user.coins=coins+amount; label="loan"
        elif action=="repay":
            repay = loan if amount==0 else min(amount,loan)
            if loan<=0: return {"status":"error","message":"وام فعالی نداری."}
            if coins<repay: return {"status":"error","message":"برای تسویه سکه کافی نداری."}
            user.coins=coins-repay; user.loan_balance=loan-repay; amount=repay; label="loan_repay"
        else: raise HTTPException(status_code=404,detail="Unknown bank action")
        session.add(Purchase(user_id=user.id,item_id=label,amount=int(amount or 0),status="bank_activity"))
        session.commit()
        return {"status":"success","coins":int(user.coins or 0),"bank_balance":int(user.bank_balance or 0),"loan_balance":int(user.loan_balance or 0)}
    finally: session.close()


@app.get("/api/quiz")
async def get_quiz(kind:str="intel", init_data:Optional[str]=Header(None,alias="init-data")):
    telegram_user = require_user(init_data)
    pool=[q for q in QUIZ_BANK if q["kind"]==kind] or QUIZ_BANK
    session=get_session()
    try:
        answered={str(x[0]) for x in session.query(Purchase.item_id).filter(Purchase.user_id==int(telegram_user["id"]),Purchase.item_id.like(f"{kind}-%")).all()}
    finally:
        session.close()
    fresh=[q for q in pool if q["id"] not in answered]
    q=secrets.choice(fresh or pool)
    return {"id":q["id"],"kind":q["kind"],"question":q["question"],"options":q["options"],"reward":{"coins":q["coins"],"xp":q["xp"]}}


@app.post("/api/quiz/answer/{user_id}")
async def answer_quiz(user_id:int, question_id:str, choice:int, init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id)
    q=QUIZ_BY_ID.get(question_id)
    if not q: raise HTTPException(status_code=404,detail="Question not found")
    if choice<0 or choice>=len(q["options"]): raise HTTPException(status_code=400,detail="Invalid choice")
    claim_key=f"quiz:{user_id}:{question_id}"
    session=get_session()
    try:
        previous=session.query(Purchase).filter(Purchase.telegram_payment_charge_id==claim_key).first()
        if previous: return {"status":"already_answered","correct":previous.status=="quiz_correct","message":"برای این سؤال قبلاً پاسخ ثبت کردی."}
        user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404,detail="User not found")
        correct = choice==q["answer"]
        coins_reward=q["coins"] if correct else 0
        xp_reward=q["xp"] if correct else 0
        if correct:
            user.coins=int(user.coins or 0)+coins_reward
            user.xp=int(user.xp or 0)+xp_reward
            user.level=level_for_xp(user.xp)
        session.add(Purchase(user_id=user.id,item_id=question_id,amount=coins_reward,status="quiz_correct" if correct else "quiz_wrong",telegram_payment_charge_id=claim_key))
        session.commit()
        return {"status":"success","correct":correct,"correct_index":q["answer"],"explanation":q["explanation"],"reward":{"coins":coins_reward,"xp":xp_reward},"user":{"coins":int(user.coins or 0),"xp":int(user.xp or 0),"level":int(user.level or 1)}}
    finally: session.close()


@app.get("/api/leaderboard")
async def get_leaderboard(init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data); session=get_session()
    try:
        users=session.query(User).order_by(User.coins.desc()).limit(10).all()
        return [{"rank":i+1,"name":u.first_name or "کاربر","coins":int(u.coins or 0),"level":int(u.level or 1)} for i,u in enumerate(users)]
    finally: session.close()


@app.get("/api/orders/{user_id}")
async def get_orders(user_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id); session=get_session()
    try: return [serialize_order(o) for o in session.query(Order).filter(Order.user_id==user_id).order_by(Order.created_at.desc()).limit(50).all()]
    finally: session.close()


@app.post("/api/orders/{user_id}/{order_id}/renew")
async def renew_order(user_id:int,order_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id); session=get_session()
    try:
        settings=load_settings(session)
        if settings["maintenance_mode"]: return {"status":"error","message":"فروشگاه موقتاً در حال بروزرسانی است."}
        order=session.query(Order).filter(Order.id==order_id,Order.user_id==user_id).with_for_update().first()
        user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not order or not user: raise HTTPException(status_code=404,detail="Order not found")
        if not str(order.item_key).isdigit(): return {"status":"error","message":"این جایزه قابل تمدید نیست."}
        item_id=int(order.item_key); item=effective_shop_items(session).get(item_id)
        if not item or item.get("kind")!="vpn": return {"status":"error","message":"این محصول قابل تمدید نیست."}
        price=int(item["price"])
        if int(user.coins or 0)<price: return {"status":"error","message":"سکه کافی برای تمدید نداری."}
        now=datetime.datetime.utcnow()
        current_expiry=order.expires_at.replace(tzinfo=None) if order.expires_at and order.expires_at.tzinfo else order.expires_at
        base=current_expiry if current_expiry and current_expiry>now else now
        order.expires_at=base+datetime.timedelta(days=int(item["days"]))
        order.status="active"
        user.coins=int(user.coins or 0)-price
        session.add(Purchase(user_id=user.id,item_id=f"renew_{item_id}",amount=price,status="coin_purchase"))
        session.commit()
        return {"status":"success","message":"اشتراک با موفقیت تمدید شد.","coins":int(user.coins or 0),"order":serialize_order(order)}
    except:
        session.rollback(); raise
    finally: session.close()


@app.get("/api/transactions/{user_id}")
async def get_transactions(user_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id); session=get_session()
    try:
        rows=session.query(Purchase).filter(Purchase.user_id==user_id).order_by(Purchase.created_at.desc()).limit(50).all()
        def tx(p):
            label_map={"daily_reward":"جایزه روزانه","bank_deposit":"واریز به بانک","bank_withdraw":"برداشت از بانک","loan":"دریافت وام","loan_repay":"تسویه وام"}
            label=label_map.get(str(p.item_id)) or (SHOP_ITEMS.get(int(p.item_id),{}).get("name") if str(p.item_id).isdigit() else str(p.item_id))
            is_spend=p.status=="coin_purchase" or str(p.item_id) in ("bank_deposit","loan_repay")
            amount=int(p.amount or 0)
            return {"id":p.id,"type":"spend" if is_spend else "earn","label":label,"amount":-amount if is_spend else amount,"date":p.created_at.isoformat() if p.created_at else None}
        return [tx(p) for p in rows]
    finally: session.close()


@app.get("/api/shop")
async def get_shop(init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data); session=get_session()
    try:
        settings=load_settings(session)
        items=effective_shop_items(session)
        return {"status":"maintenance" if settings["maintenance_mode"] else "open","items":[{"id":k,**v} for k,v in items.items()]}
    finally: session.close()


@app.get("/api/admin/overview")
async def admin_overview(init_data:Optional[str]=Header(None,alias="init-data")):
    _,session=require_admin(init_data)
    try:
        since=datetime.datetime.utcnow()-datetime.timedelta(hours=24)
        return {
            "users":session.query(User).count(),
            "groups":session.query(Group).filter(Group.is_active.is_(True)).count(),
            "purchases_24h":session.query(Purchase).filter(Purchase.created_at>=since).count(),
            "coins_in_wallets":int(session.query(func.coalesce(func.sum(User.coins),0)).scalar() or 0),
            "settings":load_settings(session),
        }
    finally: session.close()


@app.post("/api/admin/settings")
async def admin_update_settings(request: dict, init_data:Optional[str]=Header(None,alias="init-data")):
    _,session=require_admin(init_data)
    try:
        updates=request.get("settings") if isinstance(request,dict) else None
        if not isinstance(updates,dict) or not updates:
            raise HTTPException(status_code=400,detail="No settings supplied")
        invalid=set(updates)-ADMIN_SETTING_KEYS
        if invalid:
            raise HTTPException(status_code=400,detail="Unknown setting")
        for key,value in updates.items():
            default=SETTING_DEFAULTS[key]
            if isinstance(default,bool):
                if not isinstance(value,bool): raise HTTPException(status_code=400,detail=f"{key} must be boolean")
            elif isinstance(default,list):
                if not isinstance(value,list) or len(value)>500: raise HTTPException(status_code=400,detail=f"{key} must be a list")
                value=[str(item).strip()[:2000] for item in value if str(item).strip()]
            elif isinstance(default,dict):
                if not isinstance(value,dict) or len(value)>100: raise HTTPException(status_code=400,detail=f"{key} must be an object")
                if key=="wheel_weights": value={str(k)[:3]:max(0,min(1000,int(v))) for k,v in value.items() if str(k).isdigit() and isinstance(v,(int,float)) and not isinstance(v,bool)}
                else: value={str(k).upper()[:32]:max(0,min(80,int(v))) for k,v in value.items() if str(k).strip() and isinstance(v,(int,float)) and not isinstance(v,bool)}
            else:
                if isinstance(value,bool) or not isinstance(value,(int,float)): raise HTTPException(status_code=400,detail=f"{key} must be numeric")
                value=int(value)
                if value<0 or value>10_000_000: raise HTTPException(status_code=400,detail=f"{key} out of range")
            row=session.query(AppSetting).filter(AppSetting.key==key).first()
            if row: row.value=value; row.updated_at=datetime.datetime.utcnow()
            else: session.add(AppSetting(key=key,value=value,updated_at=datetime.datetime.utcnow()))
        session.commit()
        return {"status":"success","settings":load_settings(session)}
    except:
        session.rollback()
        raise
    finally: session.close()


@app.get("/api/games")
async def get_games(init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data); return [{"id":"intel","name":"تست هوش","active":True},{"id":"logic","name":"معمای منطقی","active":True},{"id":"flag","name":"حدس پرچم","active":True}]


@app.post("/api/games/session/{user_id}/{game_key}")
async def create_game_session(user_id:int,game_key:str,request:dict=None,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id)
    if game_key not in GAME_LIMITS: raise HTTPException(status_code=404,detail="Game not supported")
    session=get_session()
    try:
        now=datetime.datetime.utcnow()
        recent=session.query(GameSession).filter(GameSession.user_id==user_id,GameSession.created_at>=now-datetime.timedelta(hours=1)).count()
        if recent>=30: raise HTTPException(status_code=429,detail="تعداد اجرای بازی بیش از حد مجاز است.")
        token=secrets.token_urlsafe(32);token_hash=hashlib.sha256(token.encode()).hexdigest()
        row=GameSession(token_hash=token_hash,user_id=user_id,game_key=game_key,started_at=now,expires_at=now+datetime.timedelta(hours=2),client_nonce=str((request or {}).get("nonce") or "")[:100] or None)
        session.add(row);session.commit()
        return {"token":token,"expires_in":7200,"game_key":game_key}
    finally:session.close()


@app.post("/api/games/score/{user_id}")
async def submit_game_score(user_id:int,request:dict,init_data:Optional[str]=Header(None,alias="init-data")):
    token=str(request.get("token") or "")
    try: score=int(request.get("score") or 0);duration=int(request.get("duration_seconds") or 0)
    except (TypeError,ValueError): raise HTTPException(status_code=400,detail="Invalid score payload")
    if not token or len(token)>200: raise HTTPException(status_code=400,detail="Invalid game session")
    session=get_session()
    try:
        now=datetime.datetime.utcnow();token_hash=hashlib.sha256(token.encode()).hexdigest()
        game_session=session.query(GameSession).filter(GameSession.token_hash==token_hash).with_for_update().first()
        if not game_session or game_session.user_id!=user_id or game_session.used_at or game_session.expires_at.replace(tzinfo=None)<now: raise HTTPException(status_code=400,detail="Game session expired or used")
        limits=GAME_LIMITS.get(game_session.game_key)
        elapsed=max(0,int((now-game_session.started_at.replace(tzinfo=None)).total_seconds()))
        if not limits or score<0 or score>limits["max_score"] or duration<limits["min_seconds"] or duration>elapsed+15: raise HTTPException(status_code=400,detail="Score verification failed")
        game_session.used_at=now
        row=GameScore(user_id=user_id,game_key=game_session.game_key,score=score,duration_seconds=duration,session_id=game_session.id,verified=True,created_at=now)
        session.add(row);session.commit()
        return {"status":"success","score":score,"verified":True}
    except:
        session.rollback();raise
    finally:session.close()


@app.get("/api/games/leaderboard/{game_key}")
async def game_leaderboard(game_key:str,period:str="weekly",init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data)
    if game_key not in GAME_LIMITS: raise HTTPException(status_code=404,detail="Game not supported")
    session=get_session()
    try:
        query=session.query(GameScore,User).join(User,User.id==GameScore.user_id).filter(GameScore.game_key==game_key,GameScore.verified.is_(True))
        if period=="weekly":
            now=datetime.datetime.utcnow();start=(now-datetime.timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0);query=query.filter(GameScore.created_at>=start)
        rows=query.order_by(GameScore.score.desc(),GameScore.created_at.asc()).limit(20).all()
        best={}
        for score_row,user in rows:
            if user.id not in best: best[user.id]={"name":user.first_name or "کاربر","score":int(score_row.score),"created_at":score_row.created_at.isoformat()}
        return [{"rank":i+1,**item} for i,item in enumerate(list(best.values())[:10])]
    finally:session.close()


@app.get("/api/groups/{user_id}")
async def get_user_groups(user_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id); session=get_session()
    try:
        groups=session.query(Group).filter(Group.is_active.is_(True)).limit(10).all()
        return [{"id":g.id,"title":g.title,"settings":{"welcome":g.welcome_enabled,"ai":g.ai_enabled,"antispam":g.antispam_enabled}} for g in groups]
    finally: session.close()


@app.get("/api/stats")
async def get_stats():
    session=get_session()
    try: return {"total_users":session.query(User).count(),"total_groups":session.query(Group).count()}
    finally: session.close()


@app.post("/api/shop/buy/{user_id}")
async def buy_item(user_id:int,item_id:int,coupon_code:str="",init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id)
    session=get_session()
    try:
        settings=load_settings(session)
        if settings["maintenance_mode"]: return {"status":"error","message":"فروشگاه موقتاً در حال بروزرسانی است."}
        item=effective_shop_items(session).get(item_id)
        if not item: raise HTTPException(status_code=404,detail="Item not found")
        user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404,detail="User not found")
        coupon=(coupon_code or "").strip().upper()
        discount=0
        if coupon:
            coupons=settings.get("coupon_codes") or {}
            if coupon not in coupons: return {"status":"error","message":"کد تخفیف معتبر نیست."}
            discount=max(0,min(80,int(coupons[coupon])))
        original_price=int(item["price"])
        final_price=max(1,round(original_price*(100-discount)/100))
        if int(user.coins or 0)<final_price: return {"status":"error","message":"سکه کافی نداری."}
        user.coins=int(user.coins or 0)-final_price
        now=datetime.datetime.utcnow()
        expires_at=now+datetime.timedelta(days=int(item["days"])) if item.get("days") else None
        metadata={key:item[key] for key in ("kind","days","volume","devices","region","warranty") if key in item}
        metadata.update({"original_price":original_price,"discount_percent":discount,"coupon":coupon or None})
        order=Order(user_id=user.id,item_key=str(item_id),item_name=item["name"],price=final_price,status="active" if item.get("kind")=="vpn" else "registered",created_at=now,expires_at=expires_at,metadata_json=metadata)
        if item.get("kind")=="vip":
            current_vip=user.vip_until.replace(tzinfo=None) if user.vip_until and user.vip_until.tzinfo else user.vip_until
            vip_base=current_vip if current_vip and current_vip>now else now
            user.vip_until=vip_base+datetime.timedelta(days=int(item["days"]))
            order.status="active"
        session.add(order)
        session.add(Purchase(user_id=user.id,item_id=str(item_id),amount=final_price,status="coin_purchase"))
        session.commit()
        return {"status":"success","message":f"{item['name']} با موفقیت خریداری شد.","coins":int(user.coins or 0),"discount_percent":discount,"order":serialize_order(order)}
    except:
        session.rollback(); raise
    finally: session.close()
