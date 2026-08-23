import hashlib
import hmac
import os
import time
from urllib.parse import quote


BASE_URL=os.getenv("MINI_APP_URL","https://isectorland-miniapp.vercel.app").split("?",1)[0]


def create_launch_token(user_id:int,ttl:int=3600)->str:
    expires=int(time.time())+ttl
    payload=f"{int(user_id)}.{expires}"
    signature=hmac.new(os.getenv("BOT_TOKEN","").encode(),payload.encode(),hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_launch_token(token:str):
    try:
        uid,expires,signature=token.split(".",2);payload=f"{int(uid)}.{int(expires)}"
        expected=hmac.new(os.getenv("BOT_TOKEN","").encode(),payload.encode(),hashlib.sha256).hexdigest()
        if int(expires)<int(time.time()) or not hmac.compare_digest(expected,signature):return None
        return {"id":int(uid),"first_name":"کاربر سکتور"}
    except Exception:return None


def create_launch_url(user_id:int)->str:
    return f"{BASE_URL}/?sectorLaunch={quote(create_launch_token(user_id))}&v=20260823-5"
