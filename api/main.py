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
from bot.database.models import User, Group, Purchase, AppSetting
from api.quiz_bank import QUIZ_BANK
from bot.modules.ai import get_ai_response, get_sector_prompt

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
    1: {"name": "VPN یک ماهه", "price": 15000},
    2: {"name": "VPN سه ماهه", "price": 40000},
    3: {"name": "پک استیکر اختصاصی", "price": 8000},
    4: {"name": "لقب سفارشی در گروه", "price": 25000},
    5: {"name": "VPN شش ماهه", "price": 75000},
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
    "daily_reward": 50,
    "vip_daily_reward": 75,
    "wheel_cooldown_hours": 24,
    "referral_reward": 250,
    "weekly_tournament_enabled": False,
}
ADMIN_SETTING_KEYS = set(SETTING_DEFAULTS)
WEATHER_LABELS = {0:"صاف",1:"عمدتاً صاف",2:"نیمه‌ابری",3:"ابری",45:"مه‌آلود",48:"مه یخ‌زن",51:"نم‌نم باران",53:"باران ریز",55:"باران شدید",61:"باران",63:"باران متوسط",65:"باران شدید",71:"برف",73:"برف متوسط",75:"برف شدید",80:"رگبار",81:"رگبار متوسط",82:"رگبار شدید",95:"رعدوبرق"}


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
    return items


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
        if used>=30: raise HTTPException(status_code=429,detail="سقف استفاده ساعتی دستیار پر شده است.")
        history=request.get("history") if isinstance(request.get("history"),list) else []
        history=[{"role":str(x.get("role")),"content":str(x.get("content"))[:1200]} for x in history[-6:] if isinstance(x,dict) and x.get("role") in ("user","assistant")]
        prompt=get_sector_prompt(type("MiniUser",(),{"id":user_id,"first_name":telegram_user.get("first_name") or "کاربر"})())
        if mode=="translate": prompt="متن را اگر فارسی است به انگلیسی و اگر غیرفارسی است به فارسی ترجمه کن. فقط ترجمه را برگردان."
        response=await get_ai_response(prompt,message,history=history)
        if not response: raise HTTPException(status_code=503,detail="دستیار موقتاً در دسترس نیست.")
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
        return {"id":user.id,"first_name":user.first_name,"username":user.username,"coins":int(user.coins or 0),"bank_balance":int(user.bank_balance or 0),"loan_balance":int(user.loan_balance or 0),"xp":int(user.xp or 0),"level":int(user.level or 1),"rank":rank,"joined_at":user.joined_at.isoformat() if user.joined_at else None,"achievements":["عضو قدیمی"] if user.joined_at and (datetime.datetime.utcnow()-user.joined_at.replace(tzinfo=None)).days>30 else [],"orders_count":orders_count,"total_spent":int(total_spent),"referrals":0,"is_admin":is_platform_admin(session,user.id),"vip_until":user.vip_until.isoformat() if user.vip_until else None}
    finally: session.close()


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
        cooldown_hours = max(1, min(168, int(load_settings(session)["wheel_cooldown_hours"])))
        if last_time and now - last_time < datetime.timedelta(hours=cooldown_hours):
            remaining = datetime.timedelta(hours=cooldown_hours) - (now - last_time)
            return {"status":"error","message":"گردونه امروز را چرخاندی.","remaining_seconds":int(remaining.total_seconds())}

        prize_index = secrets.randbelow(len(WHEEL_PRIZES))
        prize = WHEEL_PRIZES[prize_index]
        coins = int(prize.get("coins", 0))
        if coins:
            user.coins = int(user.coins or 0) + coins
        session.add(Purchase(
            user_id=user.id,
            item_id="wheel_" + prize["kind"],
            amount=coins,
            status="reward",
        ))
        session.commit()
        message = "جایزه به حسابت اضافه شد."
        if prize["kind"] in ("config", "proxy"):
            message = "جایزه ثبت شد؛ برای تحویل از بخش پشتیبانی پیام بده."
        return {"status":"success","index":prize_index,"prize":prize,"coins":int(user.coins or 0),"message":message}
    finally:
        session.close()


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
    try: return [serialize_purchase(p) for p in session.query(Purchase).filter(Purchase.user_id==user_id).order_by(Purchase.created_at.desc()).limit(50).all()]
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
async def buy_item(user_id:int,item_id:int,init_data:Optional[str]=Header(None,alias="init-data")):
    require_user(init_data,user_id)
    session=get_session()
    try:
        settings=load_settings(session)
        if settings["maintenance_mode"]: return {"status":"error","message":"فروشگاه موقتاً در حال بروزرسانی است."}
        item=effective_shop_items(session).get(item_id)
        if not item: raise HTTPException(status_code=404,detail="Item not found")
        user=session.query(User).filter(User.id==user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404,detail="User not found")
        if int(user.coins or 0)<item["price"]: return {"status":"error","message":"سکه کافی نداری."}
        user.coins-=item["price"]
        session.add(Purchase(user_id=user.id,item_id=str(item_id),amount=item["price"],status="coin_purchase"))
        session.commit()
        return {"status":"success","message":f"{item['name']} با موفقیت خریداری شد.","coins":user.coins}
    finally: session.close()
