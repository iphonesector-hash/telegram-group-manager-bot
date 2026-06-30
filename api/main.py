from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import hmac, hashlib, json, os, datetime, random
from typing import Optional
from bot.database.session import get_session
from bot.database.models import User, Group
from urllib.parse import unquote

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BOT_TOKEN = os.getenv("BOT_TOKEN")

def validate_telegram_init_data(init_data: str):
    if not BOT_TOKEN or not init_data: return False
    try:
        params = init_data.split('&')
        data_check_list = []
        received_hash = None
        for p in params:
            if '=' not in p: continue
            k, v = p.split('=', 1)
            if k == 'hash': received_hash = v
            else: data_check_list.append(f"{k}={unquote(v)}")
        if not received_hash: return False
        data_check_list.sort()
        data_check_string = "\n".join(data_check_list)
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        return hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest() == received_hash
    except: return False

@app.get("/api/user/{user_id}")
async def get_user(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user: raise HTTPException(status_code=404)
        now = datetime.datetime.utcnow()
        wheel_cd = int(max(0, 86400 - (now - user.last_wheel_spin).total_seconds())) if user.last_wheel_spin else 0
        return {
            "id": user.id, "first_name": user.first_name, "coins": user.coins, "level": user.level,
            "rank": session.query(User).filter(User.coins > user.coins).count() + 1,
            "cooldowns": {"wheel": wheel_cd}
        }
    finally: session.close()

@app.post("/api/daily-claim/{user_id}")
async def claim_daily(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404)
        now = datetime.datetime.utcnow()
        if user.last_daily_claim and (now - user.last_daily_claim).days < 1:
            return {"status": "error", "message": "باید ۲۴ ساعت صبر کنید."}
        user.coins += 50
        user.last_daily_claim = now
        session.commit()
        return {"status": "success", "coins": user.coins}
    except: session.rollback(); raise
    finally: session.close()

@app.post("/api/wheel-spin/{user_id}")
async def wheel_spin(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user: raise HTTPException(status_code=404)
        now = datetime.datetime.utcnow()
        if user.last_wheel_spin and (now - user.last_wheel_spin).total_seconds() < 86400:
            return {"status": "error", "message": "۲۴ ساعت صبر کنید."}
        prizes = [10, 20, 50, 100, 200, 0, 5, 10]
        idx = random.randint(0, 7)
        user.coins += prizes[idx]
        user.last_wheel_spin = now
        session.commit()
        return {"status": "success", "reward": prizes[idx], "coins": user.coins, "index": idx, "cooldown": 86400}
    except: session.rollback(); raise
    finally: session.close()

@app.get("/api/leaderboard")
async def get_leaderboard(init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    session = get_session()
    try:
        top = session.query(User).order_by(User.coins.desc()).limit(10).all()
        return [{"rank": i+1, "name": u.first_name, "coins": u.coins, "level": u.level} for i, u in enumerate(top)]
    finally: session.close()

@app.get("/api/shop")
async def get_shop(init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    return {"items": [{"id": 1, "name": "VPN یک ماهه", "price": 1000}, {"id": 2, "name": "VPN سه ماهه", "price": 2500}]}

@app.get("/api/games")
async def get_games(init_data: Optional[str] = Header(None, alias="init-data")):
    return [{"id": "wheel", "name": "چرخونه شانس", "active": True}, {"id": "snake", "name": "مار بازی", "active": False}]

@app.get("/api/groups/{user_id}")
async def get_user_groups(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    session = get_session()
    try:
        groups = session.query(Group).limit(5).all()
        return [{"id": g.id, "title": g.title, "settings": {"ai": g.ai_enabled, "antispam": g.antispam_enabled, "welcome": g.welcome_enabled}} for g in groups]
    finally: session.close()

@app.post("/api/shop/buy/{user_id}")
async def buy_item(user_id: int, item_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data): raise HTTPException(status_code=403)
    prices = {1: 1000, 2: 2500}
    if item_id not in prices: raise HTTPException(status_code=404)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if user.coins < prices[item_id]: return {"status": "error", "message": "سکه کافی نداری!"}
        user.coins -= prices[item_id]
        session.commit()
        return {"status": "success", "message": "خرید موفق!", "coins": user.coins}
    except: session.rollback(); raise
    finally: session.close()
