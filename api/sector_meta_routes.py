from typing import Optional
from fastapi import Header, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import datetime
from api.main import app, require_user
from api.sector_v2_routes import _guard, _require_member
from bot.database.sector_meta_models import SectorAnalyticsEvent, SectorLedger, SectorWorldBoss
from bot.database.session import get_session
from bot.services import sector_meta, sector_pet as legacy, sector_v2
from bot.utils.helpers import OWNER_ID

@app.get('/api/sector-meta/{user_id}')
async def get_sector_meta(user_id:int, init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        sector_meta.analytics(session,user_id,'meta_view');data=sector_meta.meta_snapshot(session,user_id);session.commit();return data
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.post('/api/sector-meta/{user_id}/claim/{kind}/{key}')
async def claim_sector_reward(user_id:int,kind:str,key:str,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data)
    if kind not in {'mission','quest'}:raise HTTPException(status_code=400,detail='نوع جایزه نامعتبر است')
    session=get_session()
    try:
        result=sector_meta.claim_reward(session,user_id,kind,key)
        if result.get('status')=='success':session.commit()
        else:session.rollback()
        return result
    except IntegrityError:
        session.rollback();return {'status':'error','message':'این جایزه همزمان دریافت شده؛ دوباره قابل دریافت نیست.'}
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.post('/api/sector-meta/{user_id}/boss/attack')
async def attack_sector_boss(user_id:int,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        seeded=sector_meta.ensure_boss(session);session.flush();session.query(SectorWorldBoss).filter(SectorWorldBoss.id==seeded.id).with_for_update().first()
        result=sector_meta.attack_boss(session,user_id)
        if result.get('status')=='success':session.commit()
        else:session.rollback()
        return result
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.post('/api/sector-meta/{user_id}/story/advance')
async def advance_sector_story(user_id:int,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        result=legacy.story_action(session,user_id)
        if result.get('status')=='success':
            sector_meta.analytics(session,user_id,'story_advance',payload={'chapter':int((result.get('pet') or {}).get('story_chapter') or 1)});session.commit();pet=legacy.get_or_create_pet(session,user_id);result['pet']=sector_v2.serialize_pet(pet)
        else:session.rollback()
        return result
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.get('/api/sector-season-leaderboard')
async def sector_season_leaderboard(init_data:Optional[str]=Header(None,alias='init-data')):
    telegram_user=require_user(init_data);await _require_member(int(telegram_user['id']));session=get_session()
    try:return sector_meta.season_leaderboard(session)
    finally:session.close()

@app.get('/api/sector-meta/{user_id}/ledger')
async def sector_ledger(user_id:int,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        rows=session.query(SectorLedger).filter(SectorLedger.user_id==user_id).order_by(SectorLedger.created_at.desc()).limit(50).all()
        return [{'id':r.id,'kind':r.kind,'amount':int(r.amount or 0),'balance_after':int(r.balance_after or 0),'ref_type':r.ref_type,'ref_key':r.ref_key,'metadata':r.metadata_json or {},'created_at':r.created_at.isoformat()} for r in rows]
    finally:session.close()

@app.post('/api/sector-meta/{user_id}/shop/{item_key}/sell')
async def sell_sector_item(user_id:int,item_key:str,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        result=sector_meta.sell_item(session,user_id,item_key)
        if result.get('status')=='success':session.commit()
        else:session.rollback()
        return result
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.post('/api/sector-meta/{user_id}/evolution/{path_key}')
async def choose_sector_evolution(user_id:int,path_key:str,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        result=legacy.choose_evolution(session,user_id,path_key)
        if result.get('status')=='success':
            sector_meta.analytics(session,user_id,'evolution_choose',payload={'path':path_key});session.commit();pet=legacy.get_or_create_pet(session,user_id);result['pet']=sector_v2.serialize_pet(pet)
        else:session.rollback()
        return result
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.post('/api/sector-meta/{user_id}/season/claim-previous')
async def claim_previous_sector_season(user_id:int,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data);session=get_session()
    try:
        result=sector_meta.claim_previous_season_reward(session,user_id)
        if result.get('status')=='success':session.commit()
        else:session.rollback()
        return result
    except IntegrityError:
        session.rollback();return {'status':'error','message':'جایزه فصل قبلاً دریافت شده است.'}
    except Exception:
        session.rollback();raise
    finally:session.close()

@app.get('/api/sector-meta-admin/{user_id}/analytics')
async def sector_meta_analytics(user_id:int,init_data:Optional[str]=Header(None,alias='init-data')):
    await _guard(user_id,init_data)
    if int(user_id)!=int(OWNER_ID):raise HTTPException(status_code=403,detail='Owner only')
    session=get_session()
    try:
        start=datetime.datetime.utcnow()-datetime.timedelta(days=7);rows=session.query(SectorAnalyticsEvent.event,func.count(SectorAnalyticsEvent.id)).filter(SectorAnalyticsEvent.created_at>=start).group_by(SectorAnalyticsEvent.event).order_by(func.count(SectorAnalyticsEvent.id).desc()).all();return {'window_days':7,'events':[{'event':event,'count':int(count)} for event,count in rows]}
    finally:session.close()
