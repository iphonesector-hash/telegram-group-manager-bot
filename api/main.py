from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
import httpx
import hmac
import hashlib
import json
import os
import time
import datetime
from typing import Optional
from urllib.parse import unquote

from bot.database.session import get_session
from bot.database.models import User, Group, Purchase

app = FastAPI(title="iSectorLand Unified API", version="3.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAX_INIT_DATA_AGE = int(os.getenv("TELEGRAM_INIT_DATA_MAX_AGE", "3600"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.1-8b-instant")
AI_FALLBACK_MODELS = ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]

SHOP_ITEMS = {
    1: {"name": "VPN یک ماهه", "price": 1000},
    2: {"name": "VPN سه ماهه", "price": 2500},
    3: {"name": "پک استیکر اختصاصی", "price": 500},
    4: {"name": "لقب سفارشی در گروه", "price": 2000},
}


class RewriteJobRequest(BaseModel):
    job_id: str


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


@app.post("/api/internal/news-rewrite")
async def news_rewrite(req: RewriteJobRequest):
    """One-shot capability bridge: only a fresh pending DB job can invoke Groq."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="Groq API key not configured")

    session = get_session()
    try:
        claimed = session.execute(
            text(
                """
                update sectorland_ai_rewrite_jobs
                   set status='processing'
                 where id=cast(:job_id as uuid)
                   and status='pending'
                   and expires_at > now()
                returning raw_text, topic
                """
            ),
            {"job_id": req.job_id},
        ).mappings().first()
        session.commit()
    except Exception:
        session.rollback()
        session.close()
        raise HTTPException(status_code=404, detail="Invalid or expired rewrite job")

    if not claimed:
        session.close()
        raise HTTPException(status_code=404, detail="Invalid or expired rewrite job")

    raw_text = str(claimed["raw_text"])
    topic = str(claimed["topic"])
    system_prompt = (
        "تو ویراستار حرفه‌ای کانال فارسی SectorLand هستی. متن ورودی را بدون جعل اطلاعات، "
        "به فارسی روان، کوتاه، دقیق و خوش‌خوان بازنویسی کن. لحن متناسب با موضوع باشد. "
        "تبلیغ، دعوت به کانال منبع، نام کاربری منبع، t.me و لینک تلگرامی منبع را حذف کن. "
        "اگر لینک رسمی غیرتلگرامیِ خود سرویس/سایت در متن هست و برای کاربر مفید است حفظش کن. "
        "از تیتر جذاب و ایموجی کم و مرتبط استفاده کن، اما شلوغ و زرد ننویس. "
        "هیچ ادعای جدیدی که در متن نیست اضافه نکن. فقط متن نهایی پست را برگردان."
    )
    user_prompt = f"موضوع: {topic}\n\nمتن خام:\n{raw_text[:6000]}"

    models = []
    for model in [AI_MODEL, *AI_FALLBACK_MODELS]:
        if model and model not in models:
            models.append(model)

    last_error = "AI request failed"
    output = None
    used_model = None
    async with httpx.AsyncClient(timeout=35.0) as client:
        for model in models:
            try:
                response = await client.post(
                    f"{GROQ_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "temperature": 0.35,
                        "max_tokens": 1000,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    },
                )
                if response.status_code >= 400:
                    last_error = f"{model}: HTTP {response.status_code}"
                    continue
                data = response.json()
                candidate = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
                if candidate:
                    output = candidate
                    used_model = model
                    break
            except Exception as exc:
                last_error = f"{model}: {type(exc).__name__}"

    try:
        if output:
            session.execute(
                text(
                    """
                    update sectorland_ai_rewrite_jobs
                       set status='done', result_text=:result, used_at=now(), error=null
                     where id=cast(:job_id as uuid)
                    """
                ),
                {"job_id": req.job_id, "result": output},
            )
            session.commit()
            return {"ok": True, "text": output, "model": used_model}

        session.execute(
            text(
                """
                update sectorland_ai_rewrite_jobs
                   set status='failed', error=:error, used_at=now()
                 where id=cast(:job_id as uuid)
                """
            ),
            {"job_id": req.job_id, "error": last_error[:500]},
        )
        session.commit()
        raise HTTPException(status_code=502, detail=last_error)
    finally:
        session.close()


@app.get("/api/user/{user_id}")
async def get_user(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        rank = session.query(User).filter(User.coins > user.coins).count() + 1
        return {
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username,
            "coins": user.coins,
            "bank_balance": user.bank_balance,
            "loan_balance": user.loan_balance,
            "xp": user.xp,
            "level": user.level,
            "rank": rank,
            "joined_at": user.joined_at.isoformat() if user.joined_at else None,
            "achievements": ["عضو قدیمی"] if user.joined_at and (datetime.datetime.utcnow() - user.joined_at).days > 30 else [],
        }
    finally:
        session.close()


@app.post("/api/daily-claim/{user_id}")
async def claim_daily(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        now = datetime.datetime.utcnow()
        if user.last_daily_claim and now - user.last_daily_claim < datetime.timedelta(hours=24):
            return {"status": "error", "message": "هنوز ۲۴ ساعت کامل نشده."}
        reward = 75 if user.vip_until and user.vip_until > now else 50
        user.coins += reward
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
        return [{"rank": i + 1, "name": u.first_name, "coins": u.coins, "level": u.level} for i, u in enumerate(users)]
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
        {"id": "snake", "name": "مار بازی", "active": False},
        {"id": "hokm", "name": "حکم", "active": False},
        {"id": "quiz", "name": "کوییز", "active": True},
    ]


@app.get("/api/groups/{user_id}")
async def get_user_groups(user_id: int, init_data: Optional[str] = Header(None, alias="init-data")):
    require_user(init_data, user_id)
    session = get_session()
    try:
        groups = session.query(Group).filter(Group.is_active.is_(True)).limit(10).all()
        return [{
            "id": g.id,
            "title": g.title,
            "settings": {"welcome": g.welcome_enabled, "ai": g.ai_enabled, "antispam": g.antispam_enabled},
        } for g in groups]
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
        if user.coins < item["price"]:
            return {"status": "error", "message": "سکه کافی نداری."}
        user.coins -= item["price"]
        session.add(Purchase(user_id=user.id, item_id=str(item_id), amount=item["price"], status="coin_purchase"))
        session.commit()
        return {"status": "success", "message": f"{item['name']} با موفقیت خریداری شد.", "coins": user.coins}
    finally:
        session.close()
