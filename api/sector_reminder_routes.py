import asyncio
import datetime
import hmac
import logging
import os

from fastapi import HTTPException, Request
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.error import Forbidden

from api.main import app
from bot.database.models import RuntimeState, SectorPet, User
from bot.database.session import get_session
from bot.services import sector_expansion, sector_pet

log=logging.getLogger(__name__)

def _naive(value):
    return value.replace(tzinfo=None) if value and value.tzinfo else value

@app.get('/api/cron/sector-reminders')
async def sector_reminders(request:Request):
    configured=(os.getenv('CRON_SECRET') or '').strip()
    received=request.headers.get('authorization','')
    if not configured:
        raise HTTPException(status_code=503,detail='CRON_SECRET is not configured')
    if not hmac.compare_digest(received,f'Bearer {configured}'):
        raise HTTPException(status_code=401,detail='unauthorized')
    token=(os.getenv('BOT_TOKEN') or '').strip()
    if not token:raise HTTPException(status_code=503,detail='BOT_TOKEN is not configured')
    now=datetime.datetime.utcnow();session=get_session();candidates=[]
    try:
        rows=(session.query(SectorPet,User).join(User,User.id==SectorPet.user_id).filter(SectorPet.notifications_enabled.is_(True)).order_by(SectorPet.last_interaction.asc()).limit(250).all())
        states={row.state_key:row for row in session.query(RuntimeState).filter(RuntimeState.scope=='sector_reminder').all()}
        for pet,user in rows:
            before=dict(pet.inventory or {})
            completed=[]
            for key,value in before.items():
                if not key.startswith('gear_upgrade_timer:') or sector_expansion._remaining(value,now)>0:continue
                item_key=key.split(':',1)[1]
                if before.get('gear_pending:'+item_key):completed.append(item_key)
            if completed:
                sector_expansion.normalize_pet(pet)
                titles=[sector_expansion.sector_v2.CATALOG.get(key,{}).get('title',key) for key in completed]
                text=f"✅ <b>ارتقای تجهیزات تمام شد</b>\n\n{pet.name} آماده است: «{'، '.join(titles)}» به سطح جدید رسید."
                candidates.append((pet,user,None,text,'open_shop'))
                continue
            inactive=max(0,(now-(_naive(pet.last_interaction) or now)).total_seconds()/3600)
            if inactive<18:continue
            state=states.get(str(pet.user_id));sent_raw=(state.value or {}).get('sent_at') if state else None
            try:sent_at=datetime.datetime.fromisoformat(sent_raw) if sent_raw else None
            except (TypeError,ValueError):sent_at=None
            if sent_at and (now-_naive(sent_at)).total_seconds()<22*3600:continue
            sector_pet.refresh_pet(pet,now);guide=sector_pet.care_guidance(pet,int(user.coins or 0));primary=guide['primary']
            if primary['priority']=='normal' and inactive<72:continue
            absence='خیلی وقته سراغم نیومدی…' if inactive>=48 else 'یه کوچولو به کمکت نیاز دارم.'
            cost=f"{primary['cost']} سکه" if primary['cost'] else 'رایگان'
            text=f"{primary['icon']} <b>{pet.name} صدات می‌کنه</b>\n\n{absence}\n{guide['message']}\n\n📊 وضعیت: {primary['value']}٪\n🪙 اقدام پیشنهادی: {primary['title']} · {cost}\n⭐ {guide['xp_remaining']} XP تا سطح {guide['next_level']}"
            candidates.append((pet,user,state,text,primary['action']))
        session.flush()
        keyboard=InlineKeyboardMarkup([[InlineKeyboardButton('رسیدگی به سکتور 🤖',web_app=WebAppInfo(url=os.getenv('MINI_APP_URL','https://telegram-group-manager-bot-iota.vercel.app')))]] )
        semaphore=asyncio.Semaphore(8)
        async with Bot(token=token) as bot:
            async def send(row):
                pet,user,state,text,action=row
                async with semaphore:
                    try:
                        await bot.send_message(chat_id=int(user.id),text=text,parse_mode='HTML',reply_markup=keyboard)
                        return row,'sent'
                    except Forbidden:
                        return row,'blocked'
                    except Exception as exc:
                        log.warning('Sector reminder failed for %s: %s',user.id,type(exc).__name__);return row,'failed'
            results=await asyncio.gather(*(send(row) for row in candidates))
        sent=blocked=failed=0
        for (pet,user,state,_text,action),status in results:
            if status=='blocked':pet.notifications_enabled=False;blocked+=1;continue
            if status!='sent':failed+=1;continue
            value={'sent_at':now.isoformat(),'action':action}
            if state:state.value=value
            else:session.add(RuntimeState(scope='sector_reminder',state_key=str(user.id),value=value))
            sent+=1
        session.commit();return {'ok':True,'checked':len(rows),'eligible':len(candidates),'sent':sent,'blocked':blocked,'failed':failed}
    except Exception:
        session.rollback();raise
    finally:session.close()
