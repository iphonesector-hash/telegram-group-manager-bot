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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def validate_telegram_init_data(init_data: str):
    if not BOT_TOKEN or not init_data:
        return True # For development

    try:
        from urllib.parse import parse_qs, unquote
        parsed_data = parse_qs(init_data)
        hash_str = parsed_data.get('hash', [None])[0]
        if not hash_str: return False

        data_check_list = []
        for key, value in sorted(parsed_data.items()):
            if key != 'hash':
                data_check_list.append(f"{key}={value[0]}")
        data_check_string = "\n".join(data_check_list)

        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        return calculated_hash == hash_str
    except Exception as e:
        print(f"Validation Error: {e}")
        return False

@app.get("/api/user/{user_id}")
async def get_user(user_id: int, init_data: Optional[str] = Header(None)):
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
async def claim_daily(user_id: int, init_data: Optional[str] = Header(None)):
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

    reward = 50 # Basic reward
    user.coins += reward
    user.last_daily_claim = now
    session.commit()
    session.close()
    return {"status": "success", "reward": reward}

@app.get("/api/leaderboard")
async def get_leaderboard():
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

@app.get("/api/groups/{user_id}")
async def get_user_groups(user_id: int):
    # This would normally check if user is admin in groups
    # Simplification: return some groups from DB
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
        "total_groups": session.query(Group).count(),
        "active_today": 0 # Logic to be added
    }
    session.close()
    return data
