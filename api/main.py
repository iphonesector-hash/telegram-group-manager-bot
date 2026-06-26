from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import json
import os
import time
import datetime
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
        raise HTTPException(status_code=500, detail="Bot token not configured")

    if not init_data:
        print("Validation Error: No init-data header received")
        return False

    try:
        # Standard Telegram validation:
        # 1. Parse into key-value pairs
        # 2. Extract and remove hash
        # 3. Sort keys alphabetically
        # 4. Join with \n
        # 5. Sign with secret_key derived from BOT_TOKEN

        params = init_data.split('&')
        data_check_list = []
        received_hash = None

        for p in params:
            if '=' not in p: continue
            key, value = p.split('=', 1)
            if key == 'hash':
                received_hash = value
            else:
                # IMPORTANT: Use unquote for the value as Telegram sends them encoded
                data_check_list.append(f"{key}={unquote(value)}")

        if not received_hash:
            print("Validation Error: 'hash' field missing in initData")
            return False

        data_check_list.sort()
        data_check_string = "\n".join(data_check_list)

        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash != received_hash:
            print(f"Validation Error: Hash mismatch. Received data length: {len(init_data)}")
            # print(f"DEBUG Check String: {data_check_string}")
            return False

        # Optional: Extract user id for logging
        try:
            for item in data_check_list:
                if item.startswith("user="):
                    user_json = item[5:]
                    user_data = json.loads(user_json)
                    print(f"Validation Success: User ID {user_data.get('id')} authenticated.")
                    break
        except:
            pass

        return True
    except Exception as e:
        print(f"Validation Exception: {e}")
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

    data = {
        "id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "coins": user.coins,
        "xp": user.xp,
        "level": user.level,
        "rank": rank,
        "joined_at": user.joined_at.isoformat(),
        "achievements": ["عضو قدیمی"] if (datetime.datetime.utcnow() - user.joined_at).days > 30 else []
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
    if user.last_daily_claim and (now - user.last_daily_claim).days < 1:
        session.close()
        return {"status": "error", "message": "باید ۲۴ ساعت صبر کنید."}

    reward = 50
    user.coins += reward
    user.last_daily_claim = now
    session.commit()

    current_coins = user.coins
    session.close()
    return {"status": "success", "reward": reward, "coins": current_coins}

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
            {"id": 3, "name": "پک استیکر اختصاصی", "price": 500},
            {"id": 4, "name": "لقب سفارشی در گروه", "price": 2000}
        ]
    }

@app.get("/api/games")
async def get_games(init_data: Optional[str] = Header(None, alias="init-data")):
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=403, detail="Invalid auth")

    return [
        {"id": "snake", "name": "مار بازی", "active": False},
        {"id": "hokm", "name": "حکم", "active": False},
        {"id": "quiz", "name": "کوییز", "active": False}
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

@app.get("/api/stats")
async def get_stats():
    session = get_session()
    data = {
        "total_users": session.query(User).count(),
        "total_groups": session.query(Group).count()
    }
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
