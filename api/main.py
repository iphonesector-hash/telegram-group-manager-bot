from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import json
import os
import time
import datetime
import random
from typing import Optional, List
from sqlalchemy.orm import Session
from bot.database.session import get_session
from bot.database.models import User, Group
from urllib.parse import parse_qs, unquote

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def validate_telegram_init_data(init_data: str):
    if not BOT_TOKEN:
        print("Validation Error: BOT_TOKEN not configured in environment")
        return False # Fallback to false if no token

    if not init_data:
        print("Validation Error: No init-data header received")
        return False

    try:
        params = init_data.split('&')
        data_check_list = []
        received_hash = None

        for p in params:
            if '=' not in p: continue
            key, value = p.split('=', 1)
            if key == 'hash':
                received_hash = value
            else:
                data_check_list.append(f"{key}={unquote(value)}")

        if not received_hash:
            return False

        data_check_list.sort()
        data_check_string = "\n".join(data_check_list)

        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        return calculated_hash == received_hash
    except:
        return False

@app.get("/api/user/{user_id}")
async def get_user(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    rank = session.query(User).filter(User.coins > user.coins).count() + 1

    # Calculate cooldowns
    now = datetime.datetime.utcnow()
    daily_cooldown = 0
    if user.last_daily_claim:
        diff = (now - user.last_daily_claim).total_seconds()
        if diff < 86400:
            daily_cooldown = int(86400 - diff)

    wheel_cooldown = 0
    if user.last_wheel_spin:
        diff = (now - user.last_wheel_spin).total_seconds()
        if diff < 86400:
            wheel_cooldown = int(86400 - diff)

    data = {
        "id": user.id,
        "first_name": user.first_name,
        "coins": user.coins,
        "xp": user.xp,
        "level": user.level,
        "rank": rank,
        "cooldowns": {
            "daily": daily_cooldown,
            "wheel": wheel_cooldown
        }
    }
    session.close()
    return data

@app.post("/api/daily-claim/{user_id}")
async def claim_daily(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.datetime.utcnow()
    if user.last_daily_claim:
        diff = (now - user.last_daily_claim).total_seconds()
        if diff < 86400:
            remaining = int(86400 - diff)
            session.close()
            return {"status": "error", "message": "باید ۲۴ ساعت صبر کنید.", "cooldown": remaining}

    reward = 50
    user.coins += reward
    user.last_daily_claim = now
    session.commit()

    current_coins = user.coins
    session.close()
    return {"status": "success", "reward": reward, "coins": current_coins, "cooldown": 86400}

@app.post("/api/wheel-spin/{user_id}")
async def wheel_spin(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.datetime.utcnow()
    if user.last_wheel_spin:
        diff = (now - user.last_wheel_spin).total_seconds()
        if diff < 86400:
            remaining = int(86400 - diff)
            session.close()
            return {"status": "error", "message": "چرخونه هر ۲۴ ساعت یکبار می‌چرخه.", "cooldown": remaining}

    prizes = [10, 20, 50, 100, 200, 0, 5, 10]
    reward = random.choice(prizes)

    user.coins += reward
    user.last_wheel_spin = now
    session.commit()

    res = {
        "status": "success",
        "reward": reward,
        "coins": user.coins,
        "cooldown": 86400,
        "index": prizes.index(reward) # For frontend animation
    }
    session.close()
    return res

@app.post("/api/game/dice/{user_id}")
async def game_dice(user_id: int, bet: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user or user.coins < bet:
        session.close()
        raise HTTPException(status_code=400, detail="Insufficient coins")

    dice_val = random.randint(1, 6)
    win = dice_val > 3

    if win:
        user.coins += bet
    else:
        user.coins -= bet

    session.commit()
    res = {"dice": dice_val, "win": win, "coins": user.coins}
    session.close()
    return res

@app.post("/api/game/coin/{user_id}")
async def game_coin(user_id: int, bet: int, side: str, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user or user.coins < bet:
        session.close()
        raise HTTPException(status_code=400, detail="Insufficient coins")

    result = random.choice(["heads", "tails"])
    win = result == side

    if win:
        user.coins += bet
    else:
        user.coins -= bet

    session.commit()
    res = {"result": result, "win": win, "coins": user.coins}
    session.close()
    return res

@app.get("/api/leaderboard")
async def get_leaderboard(init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()
    data = []
    for i, u in enumerate(top_users):
        data.append({
            "rank": i+1,
            "name": u.first_name,
            "coins": u.coins,
            "level": u.level
        })
    session.close()
    return data

@app.get("/api/shop")
async def get_shop(init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    return {
        "status": "open",
        "items": [
            {"id": 1, "name": "VPN یک ماهه", "price": 1000},
            {"id": 2, "name": "VPN سه ماهه", "price": 2500},
            {"id": 3, "pake": "پک استیکر اختصاصی", "price": 500},
            {"id": 4, "name": "لقب سفارشی در گروه", "price": 2000}
        ]
    }

@app.get("/api/games")
async def get_games(init_data: Optional[str] = Header(None, alias="init-data")):
    return [
        {"id": "dice", "name": "تاس انداختن", "active": True},
        {"id": "coin", "name": "شیر یا خط", "active": True},
        {"id": "wheel", "name": "چرخونه شانس", "active": True}
    ]

@app.get("/api/groups/{user_id}")
async def get_user_groups(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    session = get_session()
    groups = session.query(Group).limit(5).all()
    data = []
    for g in groups:
        data.append({
            "id": g.id,
            "title": g.title,
            "settings": {
                "welcome": g.welcome_enabled,
                "ai": g.ai_enabled,
                "antispam": g.antispam_enabled
            }
        })
    session.close()
    return data

@app.post("/api/shop/buy/{user_id}")
async def buy_item(user_id: int, item_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    shop_items = {
        1: {"name": "VPN یک ماهه", "price": 1000},
        2: {"name": "VPN سه ماهه", "price": 2500},
        3: {"name": "پک استیکر اختصاصی", "price": 500},
        4: {"name": "لقب سفارشی در گروه", "price": 2000}
    }

    if item_id not in shop_items:
        raise HTTPException(status_code=404, detail="Item not found")

    item = shop_items[item_id]

    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    if user.coins < item["price"]:
        session.close()
        return {"status": "error", "message": "سکه کافی نداری! برو تو گروه فعالیت کن."}

    user.coins -= item["price"]
    session.commit()

    current_coins = user.coins
    session.close()

    return {
        "status": "success",
        "message": f"آیتم {item['name']} با موفقیت خریداری شد!",
        "coins": current_coins
    }
