from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import json
import os
import time
import datetime
from typing import Optional
from urllib.parse import unquote
from sqlalchemy import func

from bot.database.session import get_session
from bot.database.models import User, Group, Purchase

app = FastAPI(title="iSectorLand Unified API", version="3.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAX_INIT_DATA_AGE = int(os.getenv("TELEGRAM_INIT_DATA_MAX_AGE", "3600"))

SHOP_ITEMS = {
    1: {"name": "VPN یک ماهه", "price": 1000},
    2: {"name": "VPN سه ماهه", "price": 2500},
    3: {"name": "پک استیکر اختصاصی", "price": 500},
    4: {"name": "لقب سفارشی در گروه", "price": 2000},
}


def validate_telegram_init_data(init_data: Optional[str]) -> dict:
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")
    try:
        pairs = []
        values = {}
        received_hash = None
        for part in init_data.split("&"):
            if "=" not in part:
                continue
            key, raw_value = part.split("=", 1)
            value = unquote(raw_value)
            if key == "hash":
                received_hash = value
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


def serialize_purchase(p: Purchase):
    item = SHOP_ITEMS.get(int(p.item_id)) if str(p.item_id).isdigit() else None
    return {
        "id": p.id,
        "item_id": p.item_id,
        "name": item["name"] if item else p.item_id,
        "amount": int(p.amount or 0),
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@app.get("/api/user/{user_id}")
async def get_user(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        rank = session.query(User).filter(User.coins > user.coins).count() + 1
        orders_count = session.query(Purchase).filter(Purchase.user_id == user_id).count()
        total_spent = session.query(func.coalesce(func.sum(Purchase.amount), 0)).filter(Purchase.user_id == user_id).scalar() or 0
        return {
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username,
            "coins": int(user.coins or 0),
            "bank_balance": int(user.bank_balance or 0),
            "loan_balance": int(user.loan_balance or 0),
            "xp": int(user.xp or 0),
            "level": int(user.level or 1),
            "rank": rank,
            "joined_at": user.joined_at.isoformat() if user.joined_at else None,
            "achievements": ["عضو قدیمی"] if user.joined_at and (datetime.datetime.utcnow() - user.joined_at.replace(tzinfo=None)).days > 30 else [],
            "orders_count": orders_count,
            "total_spent": int(total_spent),
            "referrals": 0,
        }
    finally:
        session.close()


@app.post("/api/daily-claim/{user_id}")
async def claim_daily(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        now = datetime.datetime.utcnow()
        last = user.last_daily_claim.replace(tzinfo=None) if user.last_daily_claim and user.last_daily_claim.tzinfo else user.last_daily_claim
        if last and now - last < datetime.timedelta(hours=24):
            remaining = datetime.timedelta(hours=24) - (now - last)
            return {"status": "error", "message": "هنوز ۲۴ ساعت کامل نشده.", "remaining_seconds": int(remaining.total_seconds())}
        vip_until = user.vip_until.replace(tzinfo=None) if user.vip_until and user.vip_until.tzinfo else user.vip_until
        reward = 75 if vip_until and vip_until > now else 50
        user.coins = int(user.coins or 0) + reward
        user.last_daily_claim = now
        session.commit()
        return {"status": "success", "reward": reward, "coins": user.coins}
    finally:
        session.close()


@app.get("/api/leaderboard")
async def get_leaderboard(init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data)
    session = get_session()
    try:
        users = session.query(User).order_by(User.coins.desc()).limit(10).all()
        return [{"rank": i + 1, "name": u.first_name or "کاربر", "coins": int(u.coins or 0), "level": int(u.level or 1)} for i, u in enumerate(users)]
    finally:
        session.close()


@app.get("/api/orders/{user_id}")
async def get_orders(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        rows = session.query(Purchase).filter(Purchase.user_id == user_id).order_by(Purchase.created_at.desc()).limit(50).all()
        return [serialize_purchase(p) for p in rows]
    finally:
        session.close()


@app.get("/api/transactions/{user_id}")
async def get_transactions(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        rows = session.query(Purchase).filter(Purchase.user_id == user_id).order_by(Purchase.created_at.desc()).limit(50).all()
        return [{
            "id": p.id,
            "type": "spend" if p.status == "coin_purchase" else "activity",
            "label": (SHOP_ITEMS.get(int(p.item_id), {}).get("name") if str(p.item_id).isdigit() else None) or str(p.item_id),
            "amount": -int(p.amount or 0) if p.status == "coin_purchase" else int(p.amount or 0),
            "date": p.created_at.isoformat() if p.created_at else None,
        } for p in rows]
    finally:
        session.close()


@app.get("/api/shop")
async def get_shop(init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data)
    return {"status": "open", "items": [{"id": k, **v} for k, v in SHOP_ITEMS.items()]}


@app.get("/api/games")
async def get_games(init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data)
    return [
        {"id": "quiz", "name": "کوییز", "active": True},
        {"id": "logic", "name": "معمای منطقی", "active": True},
        {"id": "flag", "name": "حدس پرچم", "active": True},
    ]


@app.get("/api/groups/{user_id}")
async def get_user_groups(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        groups = session.query(Group).filter(Group.is_active.is_(True)).limit(10).all()
        return [{"id": g.id, "title": g.title, "settings": {"welcome": g.welcome_enabled, "ai": g.ai_enabled, "antispam": g.antispam_enabled}} for g in groups]
    finally:
        session.close()


@app.get("/api/stats")
async def get_stats():
    session = get_session()
    try:
        return {"total_users": session.query(User).count(), "total_groups": session.query(Group).count()}
    finally:
        session.close()


@app.post("/api/shop/buy/{user_id}")
async def buy_item(user_id: int, item_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    item = SHOP_ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if int(user.coins or 0) < item["price"]:
            return {"status": "error", "message": "سکه کافی نداری."}
        user.coins -= item["price"]
        session.add(Purchase(user_id=user.id, item_id=str(item_id), amount=item["price"], status="coin_purchase"))
        session.commit()
        return {"status": "success", "message": f"{item['name']} با موفقیت خریداری شد.", "coins": user.coins}
    finally:
        session.close()
