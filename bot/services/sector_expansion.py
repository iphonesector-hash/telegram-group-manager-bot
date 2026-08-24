import datetime
import random

from bot.database.models import Purchase, SectorPetAction, SectorPetGame, User
from bot.services import sector_pet as legacy, sector_v2

UTC=datetime.timezone.utc
TUTORIAL=[
 {"id":"charge","title":"هسته را شارژ کن","detail":"با شارژ، انرژی لازم برای مأموریت‌ها تأمین می‌شود.","action":"open_care"},
 {"id":"game","title":"اولین بازی را انجام بده","detail":"بازی‌ها سکه و XP می‌دهند.","action":"open_games"},
 {"id":"reward","title":"پاداش مأموریت را بگیر","detail":"پاداش‌های آماده را در مرکز مأموریت دریافت کن.","action":"open_command"},
 {"id":"gear","title":"یک قطعه نصب کن","detail":"هر قطعه قدرت واقعی سکتور را تغییر می‌دهد.","action":"open_shop"},
 {"id":"story","title":"داستان را جلو ببر","detail":"انتخاب‌ها مسیر آینده سکتور را می‌سازند.","action":"open_growth"},
]
BASE_DEFS={
 "charger":{"title":"ایستگاه شارژ","icon":"⚡","perk":"بازیابی بهتر انرژی","base_cost":450,"hours":1},
 "lab":{"title":"آزمایشگاه","icon":"🧪","perk":"XP بیشتر از بازی","base_cost":700,"hours":2},
 "workshop":{"title":"کارگاه تعمیر","icon":"🛠️","perk":"زره و ساخت قطعه","base_cost":600,"hours":2},
 "storage":{"title":"انبار قطعات","icon":"📦","perk":"مواد و دارایی بیشتر","base_cost":500,"hours":1},
 "command":{"title":"اتاق فرمان","icon":"🛰️","perk":"پاداش مأموریت بهتر","base_cost":900,"hours":3},
}
EVENT={"id":"crystal_storm","title":"طوفان کریستالی","detail":"بازی کن، از سکتور مراقبت کن و کریستال جمع کن.","goal":12,"coins":480,"material":6}
SCHEMA_VERSION=3

def _now(): return datetime.datetime.utcnow()
def _int(value,default=0):
 try:return int(value or 0)
 except (TypeError,ValueError):return default
def _inv(pet): return dict(pet.inventory) if isinstance(pet.inventory,dict) else {}

def normalize_pet(pet):
 """Repair legacy/corrupt JSON without deleting valid owned assets."""
 changed=False;inv=_inv(pet);appearance=dict(pet.appearance) if isinstance(pet.appearance,dict) else {}
 if not isinstance(pet.inventory,dict):changed=True
 if not isinstance(pet.appearance,dict):changed=True
 for key in BASE_DEFS:
  base_key="base:"+key
  try:level=max(0,min(5,int(inv.get(base_key,0) or 0)))
  except (TypeError,ValueError):level=0;changed=True
  if inv.get(base_key,0)!=level:inv[base_key]=level;changed=True
 now=_now()
 for key in list(inv):
  if not key.startswith('gear_upgrade_timer:'):continue
  item_key=key.split(':',1)[1]
  if _remaining(inv.get(key),now)==0:
   inv['gear_level:'+item_key]=max(1,min(10,_int(inv.get('gear_pending:'+item_key),_int(inv.get('gear_level:'+item_key),1))));inv.pop('gear_pending:'+item_key,None);inv.pop(key,None);changed=True
 valid_appearance={}
 for key,value in appearance.items():
  if key in {"primary_color","secondary_color","core_color","eye_color"} and isinstance(value,str) and value.startswith("#") and len(value) in {4,7}:valid_appearance[key]=value
  elif key=="story_branch" and value in {"guardian","explorer","engineer"}:valid_appearance[key]=value
  elif value in sector_v2.CATALOG and inv.get("cosmetic:"+value):
   # Migrate legacy head/body/hand keys to the explicit component slot.
   slot=sector_v2.CATALOG[value].get("slot")
   if slot:valid_appearance[slot]=value
   if slot!=key:changed=True
  else:changed=True
 inv["system:schema_version"]=SCHEMA_VERSION
 for field in ("energy","happiness","health","hunger","cleanliness"):
  try:value=max(0,min(100,int(getattr(pet,field) or 0)))
  except (TypeError,ValueError):value=80;changed=True
  if getattr(pet,field)!=value:setattr(pet,field,value);changed=True
 pet.story_chapter=max(1,min(8,_int(pet.story_chapter,1)));pet.story_progress=max(0,_int(pet.story_progress));pet.inventory=inv;pet.appearance=valid_appearance
 return {"schema_version":SCHEMA_VERSION,"repaired":changed}
def _remaining(value,now=None):
 now=now or _now()
 if not value:return 0
 try: end=datetime.datetime.fromisoformat(str(value).replace("Z","+00:00"));end=end.replace(tzinfo=None) if end.tzinfo else end;return max(0,int((end-now).total_seconds()))
 except (TypeError,ValueError):return 0

def _tutorial_progress(session,user_id,pet,now):
 start=pet.created_at.replace(tzinfo=None) if pet.created_at and pet.created_at.tzinfo else (pet.created_at or now-datetime.timedelta(days=1))
 inv=_inv(pet);appearance=dict(pet.appearance or {})
 done={
  "charge":session.query(SectorPetAction.id).filter(SectorPetAction.user_id==user_id,SectorPetAction.action=="charge",SectorPetAction.created_at>=start).first() is not None,
  "game":session.query(SectorPetGame.id).filter(SectorPetGame.user_id==user_id,SectorPetGame.created_at>=start).first() is not None,
  "reward":any(k.startswith("tutorial:reward") for k,v in inv.items() if v),
  "gear":any(v in sector_v2.CATALOG for v in appearance.values()),
  "story":int(pet.story_progress or 0)>0 or int(pet.story_chapter or 1)>1,
 }
 steps=[{**x,"done":done[x["id"]]} for x in TUTORIAL];index=next((i for i,x in enumerate(steps) if not x["done"]),len(steps))
 return {"complete":index>=len(steps),"current":steps[index] if index<len(steps) else None,"steps":steps,"completed":sum(1 for x in steps if x["done"])}

def _base_snapshot(pet,now):
 inv=_inv(pet);out=[]
 for key,d in BASE_DEFS.items():
  level=max(0,_int(inv.get("base:"+key,0)));until=inv.get("base_timer:"+key);left=_remaining(until,now)
  if until and left==0 and inv.get("base_pending:"+key):
   level=int(inv.get("base_pending:"+key));inv["base:"+key]=level;inv.pop("base_pending:"+key,None);inv.pop("base_timer:"+key,None)
  out.append({"id":key,**d,"level":level,"max_level":5,"upgrading":left>0,"remaining_seconds":left,"next_cost":int(d["base_cost"]*(level+1)**1.35)})
 pet.inventory=inv
 return out

def _event_snapshot(session,user_id,pet,now):
 start=now-datetime.timedelta(days=7);games=session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id,SectorPetGame.created_at>=start).count();care=session.query(SectorPetAction).filter(SectorPetAction.user_id==user_id,SectorPetAction.created_at>=start).count();progress=min(EVENT["goal"],games*2+care);end=(now+datetime.timedelta(days=(6-now.weekday()))).replace(hour=23,minute=59,second=59,microsecond=0);claimed=bool(_inv(pet).get("event_claim:"+EVENT["id"]+":"+end.strftime("%Y%W")))
 return {**EVENT,"progress":progress,"complete":progress>=EVENT["goal"],"claimed":claimed,"remaining_seconds":max(0,int((end-now).total_seconds()))}

def snapshot(session,user_id):
 now=_now();pet=legacy.get_or_create_pet(session,user_id);migration=normalize_pet(pet);user=session.query(User).filter(User.id==user_id).first();base=_base_snapshot(pet,now);inv=_inv(pet);scrap=max(0,_int(inv.get("material:scrap",0)));crystal=max(0,_int(inv.get("material:crystal",0)))
 economy=[
  {"title":"شارژ انرژی","cost":35,"result":"+۲۵ انرژی","source":"مراقبت"},{"title":"تعمیر کامل","cost":55,"result":"+۲۰ سلامت","source":"مراقبت"},{"title":"بازی مهارتی","cost":0,"result":"۱۰ تا ۶۰ سکه + XP","source":"بازی‌ها"},{"title":"مأموریت روزانه","cost":0,"result":"سکه، XP و امتیاز فصل","source":"مرکز مأموریت"},
 ]
 branch=dict(pet.appearance or {}).get("story_branch") or pet.evolution_path;last_battle=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.item_id=="sector_tactical_battle").order_by(Purchase.created_at.desc()).first();battle_cooldown=0
 if last_battle:
  last_at=last_battle.created_at.replace(tzinfo=None) if last_battle.created_at and last_battle.created_at.tzinfo else last_battle.created_at;battle_cooldown=max(0,int((datetime.timedelta(minutes=10)-(now-last_at)).total_seconds()))
 return {"schema":migration,"tutorial":_tutorial_progress(session,user_id,pet,now),"base":base,"materials":{"scrap":scrap,"crystal":crystal},"event":_event_snapshot(session,user_id,pet,now),"economy":economy,"story_branch":branch,"battle_cooldown_seconds":battle_cooldown,"coins":int(user.coins or 0) if user else 0}

def command(session,user_id,action,payload=None):
 payload=payload or {};now=_now();pet=legacy.get_or_create_pet(session,user_id,lock=True);normalize_pet(pet);user=session.query(User).filter(User.id==user_id).with_for_update().first();inv=_inv(pet)
 if action=="tutorial_reward":
  tutorial=_tutorial_progress(session,user_id,pet,now)
  if tutorial["completed"]<2:return {"status":"error","message":"ابتدا شارژ و اولین بازی آموزشی را انجام بده."}
  if inv.get("tutorial:reward"):return {"status":"error","message":"پاداش آموزشی قبلاً دریافت شده است."}
  inv["tutorial:reward"]=True;user.coins=int(user.coins or 0)+150;pet.xp=int(pet.xp or 0)+60;message="۱۵۰ سکه و ۶۰ XP آموزشی دریافت شد."
 elif action=="upgrade_base":
  key=str(payload.get("key") or "");d=BASE_DEFS.get(key)
  if not d:return {"status":"error","message":"ساختمان نامعتبر است."}
  if _remaining(inv.get("base_timer:"+key),now)>0:return {"status":"error","message":"این ساختمان هنوز در حال ارتقاست."}
  level=int(inv.get("base:"+key,0) or 0)
  if level>=5:return {"status":"error","message":"این ساختمان به حداکثر سطح رسیده است."}
  cost=int(d["base_cost"]*(level+1)**1.35)
  if int(user.coins or 0)<cost:return {"status":"error","message":f"برای ارتقا {cost} سکه لازم است."}
  user.coins=int(user.coins or 0)-cost;seconds=int(d["hours"]*3600*(level+1));inv["base_pending:"+key]=level+1;inv["base_timer:"+key]=(now+datetime.timedelta(seconds=seconds)).isoformat();session.add(Purchase(user_id=user_id,item_id="sector_base:"+key,amount=cost,status="coin_purchase"));message=f"ارتقای {d['title']} شروع شد."
 elif action=="salvage":
  key=str(payload.get("key") or "");item=sector_v2.CATALOG.get(key)
  if not item or not inv.get("cosmetic:"+key):return {"status":"error","message":"این قطعه در دارایی‌های تو نیست."}
  if key in dict(pet.appearance or {}).values():return {"status":"error","message":"ابتدا قطعه را از روی سکتور بردار."}
  crafted=bool(inv.get("crafted:"+key));gain=(1 if crafted else {"common":1,"rare":2,"epic":4,"legendary":7,"mythic":12}.get(item.get("rarity"),1))+int(inv.get("base:storage",0) or 0)//2;inv.pop("cosmetic:"+key,None);inv.pop("crafted:"+key,None);inv["material:scrap"]=int(inv.get("material:scrap",0) or 0)+gain;message=f"{item['title']} به {gain} ماده اولیه تبدیل شد."
 elif action=="forge":
  if int(inv.get("material:scrap",0) or 0)<3:return {"status":"error","message":"برای ساخت قطعه ۳ ماده اولیه لازم است."}
  owned=sector_v2.owned_keys(pet);choices=[k for k,v in sector_v2.CATALOG.items() if k not in owned and v.get("rarity") in {"rare","epic"} and legacy.level_from_xp(pet.xp)>=int(v.get("min_level",1))]
  if not choices:return {"status":"error","message":"قطعه قابل ساخت تازه‌ای باقی نمانده است."}
  key=random.choice(choices);inv["material:scrap"]=int(inv.get("material:scrap",0))-3;inv["cosmetic:"+key]=True;inv["crafted:"+key]=True;message=f"ساخت موفق: {sector_v2.CATALOG[key]['title']}"
 elif action=="claim_event":
  event=_event_snapshot(session,user_id,pet,now);claim_key="event_claim:"+event["id"]+":"+(now+datetime.timedelta(days=(6-now.weekday()))).strftime("%Y%W")
  if not event["complete"]:return {"status":"error","message":"هدف رویداد هنوز کامل نشده است."}
  if inv.get(claim_key):return {"status":"error","message":"جایزه رویداد قبلاً دریافت شده است."}
  inv[claim_key]=True;inv["material:crystal"]=int(inv.get("material:crystal",0))+event["material"];user.coins=int(user.coins or 0)+event["coins"]
  reward_pool=[k for k,v in sector_v2.CATALOG.items() if not inv.get("cosmetic:"+k) and v.get("rarity") in {"rare","epic","legendary"}]
  reward_key=random.choice(reward_pool) if reward_pool else None
  if reward_key:inv["cosmetic:"+reward_key]=True
  gear_text=f" و قطعه {sector_v2.CATALOG[reward_key]['title']}" if reward_key else ""
  message=f"{event['coins']} سکه، {event['material']} کریستال{gear_text} دریافت شد."
 elif action=="story_branch":
  key=str(payload.get("key") or "")
  if key not in {"guardian","explorer","engineer"}:return {"status":"error","message":"مسیر داستانی نامعتبر است."}
  appearance=dict(pet.appearance or {});appearance["story_branch"]=key;pet.appearance=appearance;message={"guardian":"مسیر نگهبان فعال شد.","explorer":"مسیر کاوشگر فعال شد.","engineer":"مسیر مهندس فعال شد."}[key]
 elif action=="upgrade_gear":
  key=str(payload.get('key') or '');item=sector_v2.CATALOG.get(key)
  if not item or not inv.get('cosmetic:'+key):return {'status':'error','message':'این قطعه در دارایی‌های تو نیست.'}
  level=max(1,min(10,_int(inv.get('gear_level:'+key),1)))
  if level>=10:return {'status':'error','message':'این قطعه به حداکثر سطح رسیده است.'}
  if _remaining(inv.get('gear_upgrade_timer:'+key),now)>0:return {'status':'error','message':'ارتقای این قطعه هنوز در حال انجام است.'}
  cost=int(item['cost']*.35*level);materials=max(1,level//2)
  if int(user.coins or 0)<cost:return {'status':'error','message':f'برای ارتقا {cost} سکه لازم است.'}
  if _int(inv.get('material:scrap'))<materials:return {'status':'error','message':f'برای ارتقا {materials} ماده اولیه لازم است.'}
  user.coins=int(user.coins or 0)-cost;inv['material:scrap']=_int(inv.get('material:scrap'))-materials;inv['gear_pending:'+key]=level+1;inv['gear_upgrade_timer:'+key]=(now+datetime.timedelta(seconds=level*1800)).isoformat();session.add(Purchase(user_id=user_id,item_id='sector_gear_upgrade:'+key,amount=cost,status='coin_purchase'));message=f"ارتقای {item['title']} به سطح {level+1} شروع شد."
 elif action=="repair_gear":
  key=str(payload.get('key') or '');item=sector_v2.CATALOG.get(key)
  if not item or not inv.get('cosmetic:'+key):return {'status':'error','message':'قطعه معتبر پیدا نشد.'}
  wear=max(0,min(100,_int(inv.get('gear_wear:'+key),100)));cost=max(10,(100-wear)*3)
  if wear>=100:return {'status':'error','message':'این قطعه کاملاً سالم است.'}
  if int(user.coins or 0)<cost:return {'status':'error','message':f'برای تعمیر {cost} سکه لازم است.'}
  user.coins=int(user.coins or 0)-cost;inv['gear_wear:'+key]=100;session.add(Purchase(user_id=user_id,item_id='sector_gear_repair:'+key,amount=cost,status='coin_purchase'));message=f"{item['title']} کاملاً تعمیر شد."
 elif action=="save_loadout":
  slot=max(1,min(3,_int(payload.get('slot'),1)));inv['loadout:'+str(slot)]={k:v for k,v in dict(pet.appearance or {}).items() if v in sector_v2.CATALOG};message=f'چینش شماره {slot} ذخیره شد.'
 elif action=="apply_loadout":
  slot=max(1,min(3,_int(payload.get('slot'),1)));saved=inv.get('loadout:'+str(slot))
  if not isinstance(saved,dict):return {'status':'error','message':'این چینش هنوز ذخیره نشده است.'}
  appearance=dict(pet.appearance or {});appearance={k:v for k,v in appearance.items() if v not in sector_v2.CATALOG}
  for gear_slot,key in saved.items():
   if inv.get('cosmetic:'+str(key)) and key in sector_v2.CATALOG and sector_v2.CATALOG[key]['slot']==gear_slot:appearance[gear_slot]=key
  pet.appearance=appearance;message=f'چینش شماره {slot} فعال شد.'
 else:return {"status":"error","message":"فرمان توسعه نامعتبر است."}
 pet.inventory=inv;pet.updated_at=now;legacy.remember(session,user_id,"progress","ارتقای سکتور",message,3)
 return {"status":"success","message":message,"coins":int(user.coins or 0),"pet":sector_v2.serialize_pet(pet,int(user.coins or 0)),"shop":sector_v2.catalog_for(pet),"expansion":snapshot(session,user_id)}

def tactical_battle(session,user_id,target_user,move):
 if move not in {"attack","defend","overcharge"}:return {"status":"error","message":"حرکت نبرد نامعتبر است."}
 now=_now();last=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.item_id=="sector_tactical_battle").order_by(Purchase.created_at.desc()).first()
 if last:
  last_at=last.created_at.replace(tzinfo=None) if last.created_at and last.created_at.tzinfo else last.created_at;remaining=max(0,int((datetime.timedelta(minutes=10)-(now-last_at)).total_seconds()))
  if remaining:return {"status":"error","message":"سامانه نبرد در حال خنک‌شدن است.","remaining_seconds":remaining}
 pet=legacy.get_or_create_pet(session,user_id,lock=True);target=legacy.get_or_create_pet(session,target_user.id);stats=sector_v2.serialize_pet(pet).get("equipment_stats",{});enemy=sector_v2.serialize_pet(target).get("equipment_stats",{});level=legacy.level_from_xp(pet.xp);enemy_level=legacy.level_from_xp(target.xp);branch=dict(pet.appearance or {}).get("story_branch")
 move_bonus={"attack":18,"defend":12,"overcharge":25}[move];cost={"attack":5,"defend":3,"overcharge":10}[move]
 if int(pet.energy or 0)<cost:return {"status":"error","message":f"برای این حرکت {cost} انرژی لازم است."}
 pet.energy=max(0,int(pet.energy or 0)-cost);branch_bonus={"guardian":int(stats.get("defense",0))//4,"explorer":random.randint(4,14),"engineer":int(stats.get("power",0))//4}.get(branch,0);score=level*4+int(stats.get("power",0))+int(stats.get("defense",0))//2+move_bonus+branch_bonus+random.randint(1,18);enemy_score=enemy_level*4+int(enemy.get("power",0))+int(enemy.get("defense",0))+random.randint(5,25);won=score>=enemy_score;reward=45 if won else 10;user=session.query(User).filter(User.id==user_id).with_for_update().first();user.coins=int(user.coins or 0)+reward;pet.xp=int(pet.xp or 0)+(25 if won else 8);inv=_inv(pet)
 for key in dict(pet.appearance or {}).values():
  if key in sector_v2.CATALOG:inv['gear_wear:'+key]=max(0,_int(inv.get('gear_wear:'+key),100)-random.randint(1,3))
 pet.inventory=inv;session.add(Purchase(user_id=user_id,item_id="sector_tactical_battle",amount=reward,status="reward",created_at=now));return {"status":"success","message":"پیروزی تاکتیکی!" if won else "این دور را باختی؛ تجهیزاتت را تقویت کن.","won":won,"cooldown_seconds":600,"rounds":[{"title":"قدرت تو","value":score},{"title":"قدرت حریف","value":enemy_score},{"title":"پاداش","value":reward}],"coins":int(user.coins or 0),"pet":sector_v2.serialize_pet(pet,int(user.coins or 0))}
