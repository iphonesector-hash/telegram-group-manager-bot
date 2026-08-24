import datetime
from collections import defaultdict
from sqlalchemy import func, or_
from bot.database.models import Purchase, SectorPet, SectorPetAction, SectorPetGame, SectorPetMemory, SectorPetSocial, User
from bot.database.sector_meta_models import SectorAnalyticsEvent, SectorBossHit, SectorLedger, SectorRewardClaim, SectorWorldBoss
from bot.services import sector_pet as legacy

MISSION_DEFS = {
    'daily_care': {'title':'۳ مراقبت امروز','kind':'daily','target':3,'coins':40,'xp':20,'season':20,'metric':'care'},
    'daily_game': {'title':'یک بازی امروز','kind':'daily','target':1,'coins':25,'xp':15,'season':15,'metric':'game'},
    'daily_social': {'title':'یک تعامل اجتماعی','kind':'daily','target':1,'coins':30,'xp':15,'season':20,'metric':'social'},
    'daily_chat': {'title':'یک گفت‌وگو با سکتور','kind':'daily','target':1,'coins':20,'xp':15,'season':10,'metric':'chat'},
    'weekly_shop': {'title':'یک خرید فروشگاهی','kind':'weekly','target':1,'coins':80,'xp':35,'season':45,'metric':'shop'},
    'weekly_memory': {'title':'سه بازی مدار حافظه','kind':'weekly','target':3,'coins':90,'xp':40,'season':50,'metric':'memory_game'},
}
QUEST_DEFS = {
    'repair_protocol': {'title':'پروتکل بازسازی','hint':'به سطح ۵ برس','coins':120,'xp':80,'season':60},
    'collector': {'title':'کلکسیونر قطعات','hint':'۳ آیتم ظاهری داشته باش','coins':150,'xp':90,'season':80},
    'bond_link': {'title':'پیوند پایدار','hint':'Bond سطح ۲ با یک کاربر بساز','coins':140,'xp':80,'season':70},
    'story_runner': {'title':'سیگنال داستانی','hint':'به فصل دوم داستان برس','coins':160,'xp':100,'season':90},
    'boss_hunter': {'title':'شکارچی Void','hint':'۵۰۰ Damage به Boss بزن','coins':180,'xp':120,'season':100},
}

def utcnow(): return datetime.datetime.utcnow()

def month_window(now=None):
    now=now or utcnow();start=now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    end=(start.replace(day=28)+datetime.timedelta(days=4)).replace(day=1)
    return start,end,start.strftime('%Y-%m')

def day_window(now=None):
    now=now or utcnow();start=now.replace(hour=0,minute=0,second=0,microsecond=0);return start,start+datetime.timedelta(days=1),start.strftime('%Y%m%d')

def week_window(now=None):
    now=now or utcnow();start=(now-datetime.timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0);return start,start+datetime.timedelta(days=7),start.strftime('%Y%m%d')

def ledger(session,user_id,kind,amount,balance_after,ref_type=None,ref_key=None,metadata=None):
    session.add(SectorLedger(user_id=user_id,kind=kind,amount=int(amount),balance_after=int(balance_after),ref_type=ref_type,ref_key=ref_key,metadata_json=metadata or {}))

def analytics(session,user_id,event,context='miniapp',payload=None):
    session.add(SectorAnalyticsEvent(user_id=user_id,event=event,context=context,payload=payload or {}))

def _ledger_missing(session,user_id,ref_type,ref_key):
    return session.query(SectorLedger.id).filter_by(user_id=user_id,ref_type=ref_type,ref_key=ref_key).first() is None

def sync_ledger(session,user_id):
    user=session.query(User).filter(User.id==user_id).first();balance=int(user.coins or 0) if user else 0
    purchases=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.item_id.like('sector_cosmetic:%')).order_by(Purchase.created_at.desc()).limit(80).all()
    for p in purchases:
        key=str(p.id)
        if _ledger_missing(session,user_id,'purchase',key):ledger(session,user_id,'shop_purchase',-abs(int(p.amount or 0)),balance,'purchase',key,{'item_id':p.item_id})
    games=session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id).order_by(SectorPetGame.created_at.desc()).limit(80).all()
    for g in games:
        key=str(g.id)
        if _ledger_missing(session,user_id,'game',key):ledger(session,user_id,'game_reward',abs(int(g.reward or 0)),balance,'game',key,{'game':g.game_key,'score':g.score})
    actions=session.query(SectorPetAction).filter(SectorPetAction.user_id==user_id,SectorPetAction.coin_cost>0).order_by(SectorPetAction.created_at.desc()).limit(100).all()
    for a in actions:
        key=str(a.id)
        if _ledger_missing(session,user_id,'care',key):ledger(session,user_id,'care_cost',-abs(int(a.coin_cost or 0)),balance,'care',key,{'action':a.action})
    social=session.query(SectorPetSocial).filter(or_(SectorPetSocial.actor_id==user_id,SectorPetSocial.target_id==user_id),SectorPetSocial.action=='gift').order_by(SectorPetSocial.created_at.desc()).limit(80).all()
    for r in social:
        role='actor' if int(r.actor_id)==int(user_id) else 'target';key=f'{r.id}:{role}'
        if _ledger_missing(session,user_id,'social_gift',key):ledger(session,user_id,'gift_sent' if role=='actor' else 'gift_received',-50 if role=='actor' else 50,balance,'social_gift',key,{'other_user_id':int(r.target_id if role=='actor' else r.actor_id)})

def compact_memories(session,user_id):
    total=session.query(SectorPetMemory).filter(SectorPetMemory.user_id==user_id).count()
    if total<=120:return 0
    rows=session.query(SectorPetMemory).filter(SectorPetMemory.user_id==user_id,SectorPetMemory.importance<4).order_by(SectorPetMemory.created_at.desc()).offset(80).limit(80).all()
    if not rows:return 0
    summary=' | '.join((r.title+': '+r.detail)[:180] for r in rows[:12])[:1600]
    session.add(SectorPetMemory(user_id=user_id,kind='memory_summary',title='خلاصه حافظه قدیمی',detail=summary,importance=3))
    ids=[r.id for r in rows];session.query(SectorPetMemory).filter(SectorPetMemory.id.in_(ids)).delete(synchronize_session=False);return len(ids)

def _metric(session,user_id,metric,start,end):
    if metric=='care': return session.query(SectorPetAction).filter(SectorPetAction.user_id==user_id,SectorPetAction.created_at>=start,SectorPetAction.created_at<end,SectorPetAction.action.in_(['charge','play','train','learn','repair','feed','clean','sleep'])).count()
    if metric=='game': return session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id,SectorPetGame.created_at>=start,SectorPetGame.created_at<end).count()
    if metric=='memory_game': return session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id,SectorPetGame.game_key=='circuit',SectorPetGame.created_at>=start,SectorPetGame.created_at<end).count()
    if metric=='social': return session.query(SectorPetSocial).filter(SectorPetSocial.actor_id==user_id,SectorPetSocial.created_at>=start,SectorPetSocial.created_at<end).count()
    if metric=='chat': return session.query(SectorPetMemory).filter(SectorPetMemory.user_id==user_id,SectorPetMemory.kind=='chat',SectorPetMemory.created_at>=start,SectorPetMemory.created_at<end).count()
    if metric=='shop': return session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.item_id.like('sector_cosmetic:%'),Purchase.created_at>=start,Purchase.created_at<end).count()
    return 0

def mission_snapshot(session,user_id,now=None):
    now=now or utcnow();out=[]
    for key,d in MISSION_DEFS.items():
        start,end,pkey=day_window(now) if d['kind']=='daily' else week_window(now)
        progress=_metric(session,user_id,d['metric'],start,end);claimed=session.query(SectorRewardClaim.id).filter_by(user_id=user_id,claim_key='mission:'+key,period_key=pkey).first() is not None
        out.append({'id':key,'title':d['title'],'kind':d['kind'],'progress':min(progress,d['target']),'target':d['target'],'complete':progress>=d['target'],'claimed':claimed,'reset_seconds':max(0,int((end-now).total_seconds())),'reward':{'coins':d['coins'],'xp':d['xp'],'season':d['season']}})
    return out

def bond_rows(session,user_id,limit=8):
    rows=session.query(SectorPetSocial).filter(or_(SectorPetSocial.actor_id==user_id,SectorPetSocial.target_id==user_id)).all();scores=defaultdict(lambda:{'xp':0,'interactions':0,'gifts':0,'battles':0,'visits':0})
    weights={'visit':12,'gift':35,'battle':18}
    for r in rows:
        other=int(r.target_id if int(r.actor_id)==int(user_id) else r.actor_id);s=scores[other];s['xp']+=weights.get(r.action,8);s['interactions']+=1;s[r.action+'s']+=1
    result=[]
    for other,s in sorted(scores.items(),key=lambda kv:kv[1]['xp'],reverse=True)[:limit]:
        u=session.query(User).filter(User.id==other).first();level=min(20,1+s['xp']//100);result.append({'user_id':other,'name':(u.first_name if u else 'کاربر'),'username':(u.username if u else None),'xp':s['xp'],'level':level,**{k:v for k,v in s.items() if k!='xp'}})
    return result

def _boss_damage(session,user_id,boss_id=None):
    q=session.query(func.coalesce(func.sum(SectorBossHit.damage),0)).filter(SectorBossHit.user_id==user_id)
    if boss_id:q=q.filter(SectorBossHit.boss_id==boss_id)
    return int(q.scalar() or 0)

def ensure_boss(session,now=None):
    now=now or utcnow();start,end,key=month_window(now);boss=session.query(SectorWorldBoss).filter(SectorWorldBoss.season_key==key).first()
    if boss:return boss
    pets=max(1,session.query(SectorPet).count());max_hp=max(15000,pets*6000);boss=SectorWorldBoss(season_key=key,title='VOID WARDEN',hp=max_hp,max_hp=max_hp,reward_pool=800+pets*100,active=True,started_at=start,ends_at=end);session.add(boss);session.flush();return boss

def boss_snapshot(session,user_id,now=None):
    boss=ensure_boss(session,now);top=session.query(SectorBossHit.user_id,func.sum(SectorBossHit.damage).label('dmg')).filter(SectorBossHit.boss_id==boss.id).group_by(SectorBossHit.user_id).order_by(func.sum(SectorBossHit.damage).desc()).limit(5).all();leaders=[]
    for uid,dmg in top:
        u=session.query(User).filter(User.id==uid).first();leaders.append({'user_id':int(uid),'name':u.first_name if u else 'کاربر','damage':int(dmg or 0)})
    last=session.query(SectorBossHit).filter_by(boss_id=boss.id,user_id=user_id).order_by(SectorBossHit.created_at.desc()).first();cooldown=0
    if last:
        delta=(last.created_at.replace(tzinfo=None) if last.created_at.tzinfo else last.created_at)+datetime.timedelta(minutes=30)-utcnow();cooldown=max(0,int(delta.total_seconds()))
    return {'id':boss.id,'title':boss.title,'hp':int(boss.hp),'max_hp':int(boss.max_hp),'active':bool(boss.active and boss.hp>0 and boss.ends_at.replace(tzinfo=None)>utcnow()),'reward_pool':int(boss.reward_pool),'my_damage':_boss_damage(session,user_id,boss.id),'cooldown_seconds':cooldown,'leaders':leaders,'ends_at':boss.ends_at.isoformat()}

def attack_boss(session,user_id):
    boss=ensure_boss(session);now=utcnow()
    if not boss.active or boss.hp<=0 or boss.ends_at.replace(tzinfo=None)<=now:return {'status':'error','message':'این Boss دیگر فعال نیست.'}
    last=session.query(SectorBossHit).filter_by(boss_id=boss.id,user_id=user_id).order_by(SectorBossHit.created_at.desc()).first()
    if last:
        last_at=last.created_at.replace(tzinfo=None) if last.created_at.tzinfo else last.created_at
        if now-last_at<datetime.timedelta(minutes=30):return {'status':'error','message':'سامانه حمله هنوز در حال خنک شدن است.'}
    user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=legacy.get_or_create_pet(session,user_id,lock=True)
    if int(pet.energy or 0)<10:return {'status':'error','message':'برای حمله حداقل ۱۰ انرژی لازم داری.'}
    from bot.services import sector_v2
    level=legacy.level_from_xp(int(pet.xp or 0));power_score=int(sector_v2.serialize_pet(pet).get('equipment_stats',{}).get('power_score',0));damage=min(int(boss.hp),80+level*12+int(pet.knowledge or 0)*2+power_score//8);pet.energy=max(0,int(pet.energy or 0)-10);pet.xp=int(pet.xp or 0)+10;boss.hp=max(0,int(boss.hp)-damage);session.add(SectorBossHit(boss_id=boss.id,user_id=user_id,damage=damage,created_at=now))
    reward=5
    if user_id!=legacy.OWNER_ID:user.coins=int(user.coins or 0)+reward
    if boss.hp<=0:boss.active=False;boss.defeated_at=now;reward+=100
    if boss.hp<=0 and user_id!=legacy.OWNER_ID:user.coins=int(user.coins or 0)+100
    ledger(session,user_id,'boss_reward',reward,int(user.coins or 0),'boss',str(boss.id),{'damage':damage});analytics(session,user_id,'boss_attack',payload={'damage':damage,'boss_id':boss.id})
    return {'status':'success','message':f'{damage} Damage وارد شد.','damage':damage,'coins':int(user.coins or 0),'pet':legacy.serialize_pet(pet),'boss':boss_snapshot(session,user_id)}

def season_points(session,user_id,now=None):
    now=now or utcnow();start,end,key=month_window(now);days=max(1,(now-start).days+1)
    actions=min(_metric(session,user_id,'care',start,end),days*5)*4;games=min(_metric(session,user_id,'game',start,end),days*5)*8;social=_metric(session,user_id,'social',start,end)*15;chat=min(_metric(session,user_id,'chat',start,end),days*10)*2;shop=_metric(session,user_id,'shop',start,end)*20
    boss=ensure_boss(session,now);boss_points=_boss_damage(session,user_id,boss.id)//10;claims=session.query(SectorRewardClaim).filter(SectorRewardClaim.user_id==user_id,SectorRewardClaim.created_at>=start,SectorRewardClaim.created_at<end).all();claim_points=sum(int((c.reward or {}).get('season',0)) for c in claims)
    return int(actions+games+social+chat+shop+boss_points+claim_points)

def season_snapshot(session,user_id,now=None):
    now=now or utcnow();start,end,key=month_window(now);score=season_points(session,user_id,now);rows=[]
    for pet in session.query(SectorPet).all():rows.append((pet.user_id,season_points(session,pet.user_id,now)))
    rows.sort(key=lambda x:x[1],reverse=True);rank=next((i+1 for i,(uid,_) in enumerate(rows) if int(uid)==int(user_id)),len(rows)+1)
    return {'key':key,'title':'Sector Season '+key,'points':score,'rank':rank,'participants':len(rows),'starts_at':start.isoformat(),'ends_at':end.isoformat(),'days_left':max(0,(end-now).days)}

def season_leaderboard(session,limit=30):
    now=utcnow();rows=[]
    for pet in session.query(SectorPet).all():
        u=session.query(User).filter(User.id==pet.user_id).first();rows.append({'user_id':pet.user_id,'name':pet.name,'owner':u.first_name if u else 'کاربر','points':season_points(session,pet.user_id,now),'level':legacy.level_from_xp(pet.xp)})
    rows.sort(key=lambda x:x['points'],reverse=True)
    for i,row in enumerate(rows[:limit]):row['rank']=i+1
    return rows[:limit]

def quest_snapshot(session,user_id):
    pet=legacy.get_or_create_pet(session,user_id);owned=sum(1 for k,v in (pet.inventory or {}).items() if v and str(k).startswith('cosmetic:'));bonds=bond_rows(session,user_id,20);best=max([b['level'] for b in bonds] or [0]);boss=_boss_damage(session,user_id)
    done={'repair_protocol':legacy.level_from_xp(pet.xp)>=5,'collector':owned>=3,'bond_link':best>=2,'story_runner':int(pet.story_chapter or 1)>=2,'boss_hunter':boss>=500};out=[]
    for key,d in QUEST_DEFS.items():
        claimed=session.query(SectorRewardClaim.id).filter_by(user_id=user_id,claim_key='quest:'+key,period_key='lifetime').first() is not None;out.append({'id':key,'title':d['title'],'hint':d['hint'],'complete':bool(done[key]),'claimed':claimed,'reward':{'coins':d['coins'],'xp':d['xp'],'season':d['season']}})
    return out

def claim_reward(session,user_id,kind,key):
    defs=MISSION_DEFS if kind=='mission' else QUEST_DEFS
    if key not in defs:return {'status':'error','message':'جایزه نامعتبر است.'}
    if kind=='mission':
        item=next((x for x in mission_snapshot(session,user_id) if x['id']==key),None);period=(day_window()[2] if defs[key]['kind']=='daily' else week_window()[2])
    else:item=next((x for x in quest_snapshot(session,user_id) if x['id']==key),None);period='lifetime'
    if not item or not item['complete']:return {'status':'error','message':'شرط این جایزه هنوز کامل نشده.'}
    if item['claimed']:return {'status':'error','message':'این جایزه قبلاً دریافت شده.'}
    user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=legacy.get_or_create_pet(session,user_id,lock=True);r=dict(item['reward']);command_level=int((pet.inventory or {}).get('base:command',0) or 0);bonus=command_level*5;r['coins']=int(r['coins'])*(100+bonus)//100;r['xp']=int(r['xp'])*(100+bonus)//100;user.coins=int(user.coins or 0)+int(r['coins']);pet.xp=int(pet.xp or 0)+int(r['xp']);inv=dict(pet.inventory or {});inv['story:mission_completions']=int(inv.get('story:mission_completions',0) or 0)+1;pet.inventory=inv;session.add(SectorRewardClaim(user_id=user_id,claim_key=kind+':'+key,period_key=period,reward=r));ledger(session,user_id,kind+'_reward',int(r['coins']),int(user.coins or 0),kind,key,r);analytics(session,user_id,kind+'_claim',payload={'key':key});legacy.remember(session,user_id,kind,'جایزه '+item['title'],f"{r['coins']} سکه و {r['xp']} XP دریافت شد.",3)
    return {'status':'success','message':f"جایزه دریافت شد{f'؛ اتاق فرمان {bonus}٪ پاداش اضافه داد' if bonus else ''}.",'coins':int(user.coins or 0),'pet':legacy.serialize_pet(pet)}

def unlock_snapshot(session,user_id):
    pet=legacy.get_or_create_pet(session,user_id);level=legacy.level_from_xp(int(pet.xp or 0))
    defs=[(1,'مراقبت، گفتگو و فروشگاه'),(3,'World Boss'),(5,'فروش مجدد آیتم‌ها'),(10,'انتخاب مسیر تخصصی'),(12,'ماموریت‌های پیشرفته'),(25,'تجهیزات Legendary'),(45,'تجهیزات Mythic'),(70,'فرم نهایی Mythic Sector')]
    return [{'level':lvl,'title':title,'unlocked':level>=lvl} for lvl,title in defs]

def sell_item(session,user_id,item_key):
    from bot.services import sector_v2
    item=sector_v2.CATALOG.get(item_key)
    if not item:return {'status':'error','message':'این آیتم در فروشگاه وجود ندارد.'}
    user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=legacy.get_or_create_pet(session,user_id,lock=True)
    if legacy.level_from_xp(int(pet.xp or 0))<5:return {'status':'error','message':'فروش مجدد از سطح ۵ آزاد می‌شود.'}
    inv=dict(pet.inventory or {});key='cosmetic:'+item_key
    if not inv.get(key):return {'status':'error','message':'این آیتم را در دارایی‌هایت نداری.'}
    if inv.get('crafted:'+item_key):return {'status':'error','message':'قطعه ساخته‌شده قابل فروش نیست؛ می‌توانی آن را نصب یا بازیافت کنی.'}
    resale=max(1,int(item.get('cost',0))//2);inv.pop(key,None);pet.inventory=inv;a=dict(pet.appearance or {})
    for slot,value in list(a.items()):
        if value==item_key:a.pop(slot,None)
    pet.appearance=a
    if user_id!=legacy.OWNER_ID:user.coins=int(user.coins or 0)+resale
    session.add(Purchase(user_id=user_id,item_id='sector_resale:'+item_key,amount=resale,status='coin_resale'))
    ledger(session,user_id,'shop_resale',resale,int(user.coins or 0),'resale',item_key,{'item':item_key});analytics(session,user_id,'shop_resale',payload={'item':item_key,'value':resale});legacy.remember(session,user_id,'shop','فروش '+item['title'],f'{resale} سکه از فروش مجدد دریافت شد.',2)
    return {'status':'success','message':f"{item['title']} فروخته شد و {resale} سکه گرفتی.",'coins':int(user.coins or 0),'pet':sector_v2.serialize_pet(pet),'shop':sector_v2.catalog_for(pet)}

def previous_month_window(now=None):
    now=now or utcnow();current=now.replace(day=1,hour=0,minute=0,second=0,microsecond=0);last=current-datetime.timedelta(seconds=1);start=last.replace(day=1,hour=0,minute=0,second=0,microsecond=0);return start,current,start.strftime('%Y-%m')

def _season_points_window(session,user_id,start,end,key):
    days=max(1,(end-start).days);actions=min(_metric(session,user_id,'care',start,end),days*5)*4;games=min(_metric(session,user_id,'game',start,end),days*5)*8;social=_metric(session,user_id,'social',start,end)*15;chat=min(_metric(session,user_id,'chat',start,end),days*10)*2;shop=_metric(session,user_id,'shop',start,end)*20
    boss=session.query(SectorWorldBoss).filter(SectorWorldBoss.season_key==key).first();boss_points=_boss_damage(session,user_id,boss.id)//10 if boss else 0;claims=session.query(SectorRewardClaim).filter(SectorRewardClaim.user_id==user_id,SectorRewardClaim.created_at>=start,SectorRewardClaim.created_at<end).all();claim_points=sum(int((c.reward or {}).get('season',0)) for c in claims)
    return int(actions+games+social+chat+shop+boss_points+claim_points)

def previous_season_reward_snapshot(session,user_id):
    start,end,key=previous_month_window();scores=[(p.user_id,_season_points_window(session,p.user_id,start,end,key)) for p in session.query(SectorPet).all()];scores.sort(key=lambda x:x[1],reverse=True);points=next((score for uid,score in scores if int(uid)==int(user_id)),0);rank=next((i+1 for i,(uid,_) in enumerate(scores) if int(uid)==int(user_id)),len(scores)+1)
    claimed=session.query(SectorRewardClaim.id).filter_by(user_id=user_id,claim_key='season_reward',period_key=key).first() is not None
    if points<=0:reward={'coins':0,'xp':0,'tier':'none'}
    elif rank==1:reward={'coins':1000,'xp':500,'tier':'champion'}
    elif rank==2:reward={'coins':650,'xp':350,'tier':'silver'}
    elif rank==3:reward={'coins':400,'xp':250,'tier':'bronze'}
    elif rank<=10:reward={'coins':200,'xp':150,'tier':'top10'}
    else:reward={'coins':50,'xp':50,'tier':'participant'}
    return {'season_key':key,'points':points,'rank':rank,'eligible':points>0,'claimed':claimed,'reward':reward}

def claim_previous_season_reward(session,user_id):
    snap=previous_season_reward_snapshot(session,user_id)
    if not snap['eligible']:return {'status':'error','message':'برای فصل قبل امتیاز ثبت‌شده‌ای نداری.'}
    if snap['claimed']:return {'status':'error','message':'جایزه فصل قبل قبلاً دریافت شده.'}
    user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=legacy.get_or_create_pet(session,user_id,lock=True);r=snap['reward'];user.coins=int(user.coins or 0)+int(r['coins']);pet.xp=int(pet.xp or 0)+int(r['xp']);inv=dict(pet.inventory or {});inv[f"season_badge:{snap['season_key']}:{r['tier']}"]=True;pet.inventory=inv;session.add(SectorRewardClaim(user_id=user_id,claim_key='season_reward',period_key=snap['season_key'],reward={**r,'season':0}));ledger(session,user_id,'season_reward',int(r['coins']),int(user.coins or 0),'season',snap['season_key'],r);analytics(session,user_id,'season_reward_claim',payload={'season':snap['season_key'],'rank':snap['rank']});legacy.remember(session,user_id,'season','پاداش فصل '+snap['season_key'],f"رتبه {snap['rank']}؛ {r['coins']} سکه و {r['xp']} XP",4)
    return {'status':'success','message':'جایزه فصل قبل دریافت شد.','coins':int(user.coins or 0),'pet':legacy.serialize_pet(pet)}

def notices(session,user_id):
    pet=legacy.get_or_create_pet(session,user_id);notes=[]
    from bot.services import sector_story
    narrative=sector_story.snapshot(session,user_id,pet);scene=narrative.get('scene') or {}
    if scene.get('threat'):notes.append({'kind':'alert','text':scene['threat'],'action':scene.get('route'),'objective':scene.get('objective')})
    elif scene.get('objective'):notes.append({'kind':'story','text':f"حرکت بعدی داستان: {scene['objective']}",'action':scene.get('route')})
    if int(pet.energy or 0)<25:notes.append({'kind':'care','text':'انرژی سکتور پایینه؛ بهتره استراحت یا شارژش کنی.'})
    if int(pet.hunger or 0)<30:notes.append({'kind':'care','text':'سطح سوخت غذایی سکتور پایینه.'})
    if int(pet.cleanliness or 0)<30:notes.append({'kind':'care','text':'بدنه و حسگرها نیاز به تمیزکاری دارن.'})
    claimable=sum(1 for x in mission_snapshot(session,user_id) if x['complete'] and not x['claimed'])
    if claimable:notes.append({'kind':'reward','text':f'{claimable} جایزه مأموریت آماده دریافت داری.'})
    boss=boss_snapshot(session,user_id)
    if boss['active'] and boss['cooldown_seconds']==0:notes.append({'kind':'boss','text':'World Boss آماده حمله است.'})
    return notes[:5]

def meta_snapshot(session,user_id):
    sync_ledger(session,user_id);compact_memories(session,user_id);return {'season':season_snapshot(session,user_id),'previous_season':previous_season_reward_snapshot(session,user_id),'missions':mission_snapshot(session,user_id),'quests':quest_snapshot(session,user_id),'bonds':bond_rows(session,user_id),'boss':boss_snapshot(session,user_id),'unlocks':unlock_snapshot(session,user_id),'notices':notices(session,user_id)}
