import datetime
import random
from bot.database.models import Purchase, SectorPetAction, User
from bot.services import sector_pet as legacy
from bot.utils.helpers import OWNER_ID

VISUAL_STAGES=[
 {"id":"scrap","title":"Scrap Unit","min_level":1,"min_days":0,"accent":"#8f6f4e","condition":"فرسوده"},
 {"id":"patched","title":"Patched Unit","min_level":5,"min_days":3,"accent":"#7f8da5","condition":"تعمیر اولیه"},
 {"id":"core","title":"Core Unit","min_level":12,"min_days":10,"accent":"#4ba4d9","condition":"پایدار"},
 {"id":"advanced","title":"Advanced Sector","min_level":25,"min_days":30,"accent":"#6f7cff","condition":"پیشرفته"},
 {"id":"elite","title":"Elite Sector","min_level":45,"min_days":70,"accent":"#b36df2","condition":"نخبه"},
 {"id":"mythic","title":"Mythic Sector","min_level":70,"min_days":150,"accent":"#e8c86a","condition":"فرم نهایی"},
]

CATALOG={
 "scrap_cap":{"title":"اسکنر عیب‌یاب","slot":"head","category":"ابزار","cost":180,"rarity":"common","min_level":1,"theme":"scrap"},
 "welder_mask":{"title":"ماسک جوشکاری","slot":"face","category":"صورت","cost":240,"rarity":"common","min_level":1,"theme":"industrial"},
 "patched_vest":{"title":"جلیقه وصله‌دار","slot":"body","category":"لباس","cost":300,"rarity":"common","min_level":1,"theme":"scrap"},
 "blue_shell":{"title":"بدنه آبی کلاسیک","slot":"body","category":"لباس","cost":700,"rarity":"rare","min_level":1,"theme":"legacy"},
 "gold_shell":{"title":"بدنه طلایی کلاسیک","slot":"body","category":"لباس","cost":2500,"rarity":"legendary","min_level":1,"theme":"legacy"},
 "tool_pack":{"title":"کوله ابزار","slot":"back","category":"پشت","cost":360,"rarity":"common","min_level":2,"theme":"industrial"},
 "wrench":{"title":"آچار مکانیک","slot":"hand","category":"دست","cost":420,"rarity":"common","min_level":2,"theme":"industrial"},
 "engineer_cap":{"title":"بازوی تعمیر نانو","slot":"head","category":"ابزار","cost":550,"rarity":"rare","min_level":5,"theme":"tech"},
 "round_goggles":{"title":"عینک اپتیک","slot":"face","category":"صورت","cost":620,"rarity":"rare","min_level":5,"theme":"tech"},
 "utility_jacket":{"title":"ژاکت فنی","slot":"body","category":"لباس","cost":760,"rarity":"rare","min_level":6,"theme":"tech"},
 "data_pad":{"title":"دیتاپد","slot":"hand","category":"دست","cost":850,"rarity":"rare","min_level":7,"theme":"tech"},
 "pulse_aura":{"title":"هاله پالس","slot":"aura","category":"هاله","cost":900,"rarity":"rare","min_level":8,"theme":"energy"},
 "commander_cap":{"title":"کنسول فرماندهی","slot":"head","category":"ماژول","cost":1200,"rarity":"epic","min_level":12,"theme":"command"},
 "captain_hat":{"title":"مولد سپر تاکتیکی","slot":"head","category":"ماژول","cost":1200,"rarity":"epic","min_level":1,"theme":"legacy"},
 "mono_visor":{"title":"ویزور مونو","slot":"face","category":"صورت","cost":1350,"rarity":"epic","min_level":12,"theme":"command"},
 "officer_coat":{"title":"کت فرماندهی","slot":"body","category":"لباس","cost":1600,"rarity":"epic","min_level":14,"theme":"command"},
 "mini_cape":{"title":"شنل کوتاه","slot":"back","category":"پشت","cost":1500,"rarity":"epic","min_level":1,"theme":"command"},
 "neon_wings":{"title":"بال نئونی کلاسیک","slot":"back","category":"پشت","cost":3500,"rarity":"legendary","min_level":1,"theme":"legacy"},
 "game_pad":{"title":"کنترلر تاکتیکی","slot":"hand","category":"دست","cost":1750,"rarity":"epic","min_level":1,"theme":"arcade"},
 "workshop_bg":{"title":"کارگاه متروکه","slot":"background","category":"پس‌زمینه","cost":700,"rarity":"rare","min_level":4,"theme":"scrap"},
 "neon_city_bg":{"title":"شهر نئونی","slot":"background","category":"پس‌زمینه","cost":2100,"rarity":"epic","min_level":16,"theme":"neon"},
 "neon_armor":{"title":"زره نئونی","slot":"body","category":"لباس","cost":2600,"rarity":"legendary","min_level":25,"theme":"neon"},
 "jetpack":{"title":"جت‌پک دوگانه","slot":"back","category":"پشت","cost":2900,"rarity":"legendary","min_level":27,"theme":"neon"},
 "plasma_tool":{"title":"ابزار پلاسما","slot":"hand","category":"دست","cost":2800,"rarity":"legendary","min_level":1,"theme":"neon"},
 "combat_visor":{"title":"ویزور رزمی","slot":"face","category":"صورت","cost":2450,"rarity":"legendary","min_level":24,"theme":"neon"},
 "quantum_aura":{"title":"هاله کوانتومی","slot":"aura","category":"هاله","cost":3300,"rarity":"legendary","min_level":30,"theme":"quantum"},
 "star_aura":{"title":"هاله ستاره‌ای","slot":"aura","category":"هاله","cost":4900,"rarity":"mythic","min_level":1,"theme":"elite"},
 "orbit_bg":{"title":"مدار زمین","slot":"background","category":"پس‌زمینه","cost":3200,"rarity":"legendary","min_level":30,"theme":"space"},
 "elite_crown":{"title":"هسته کریستالی","slot":"head","category":"ماژول","cost":4200,"rarity":"mythic","min_level":45,"theme":"elite"},
 "royal_chassis":{"title":"بدنه رویال","slot":"body","category":"لباس","cost":5200,"rarity":"mythic","min_level":50,"theme":"elite"},
 "ion_wings":{"title":"بال یونی","slot":"back","category":"پشت","cost":5600,"rarity":"mythic","min_level":52,"theme":"elite"},
 "command_room_bg":{"title":"اتاق فرمان","slot":"background","category":"پس‌زمینه","cost":4600,"rarity":"mythic","min_level":45,"theme":"command"},
 "halo_core":{"title":"میدان کوانتومی","slot":"head","category":"ماژول","cost":6800,"rarity":"mythic","min_level":70,"theme":"mythic"},
 "singularity_core":{"title":"هسته تکینگی","slot":"body","category":"لباس","cost":8500,"rarity":"mythic","min_level":75,"theme":"mythic"},
}

def visual_stage_for(pet):
 level=legacy.level_from_xp(int(pet.xp or 0));days=int(pet.total_care_days or 0);selected=VISUAL_STAGES[0]
 for stage in VISUAL_STAGES:
  if level>=stage['min_level'] and days>=stage['min_days']:selected=stage
 return dict(selected)

def owned_keys(pet):
 inv=dict(pet.inventory or {});return {k.split(':',1)[1] for k,v in inv.items() if v and k.startswith('cosmetic:')}

def catalog_for(pet):
 owned=owned_keys(pet);appearance=dict(pet.appearance or {});equipped=set(appearance.values());level=legacy.level_from_xp(int(pet.xp or 0));order={'common':0,'rare':1,'epic':2,'legendary':3,'mythic':4};out=[]
 for key,item in CATALOG.items():
  row={'id':key,**item,'owned':key in owned,'equipped':key in equipped,'locked':level<int(item.get('min_level',1))};out.append(row)
 return sorted(out,key=lambda r:(order.get(r['rarity'],9),r['cost'],r['title']))

def serialize_pet(pet,coins=0):
 d=legacy.serialize_pet(pet,coins);d['visual_stage']=visual_stage_for(pet);d['owned_cosmetics']=sorted(owned_keys(pet));return d

def perform_action(session,user_id,action):
 result=legacy.perform_action(session,user_id,action)
 if result.get('status')!='success':return result
 pet=legacy.get_or_create_pet(session,user_id,lock=True);pet.sleeping=action=='sleep'
 important={'feed':('care','اولین وعده انرژی','امروز دوباره شارژ غذایی گرفتم.'),'clean':('care','سرویس بدنه','بدنه و حسگرها تمیز شدند.'),'sleep':('care','حالت استراحت','برای بازیابی انرژی وارد حالت خواب شدم.')}
 if action in important:
  start=datetime.datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0);already=session.query(SectorPetAction.id).filter(SectorPetAction.user_id==user_id,SectorPetAction.action==action,SectorPetAction.created_at>=start).count()
  if already<=1:legacy.remember(session,user_id,*important[action],importance=2)
 user=session.query(User).filter(User.id==user_id).first();result['pet']=serialize_pet(pet,int(user.coins or 0) if user else 0);return result

def buy_item(session,user_id,item_key):
 item=CATALOG.get(item_key)
 if not item:return {'status':'error','message':'این آیتم در فروشگاه وجود ندارد.'}
 user=session.query(User).filter(User.id==user_id).with_for_update().first();pet=legacy.get_or_create_pet(session,user_id,lock=True)
 if not user:return {'status':'error','message':'حساب کاربر پیدا نشد.'}
 if legacy.level_from_xp(int(pet.xp or 0))<int(item['min_level']):return {'status':'error','message':f"این آیتم از سطح {item['min_level']} آزاد می‌شود."}
 inv=dict(pet.inventory or {});ik=f'cosmetic:{item_key}'
 if ik not in inv:
  cost=int(item['cost'])
  if user_id!=OWNER_ID and int(user.coins or 0)<cost:return {'status':'error','message':'سکه کافی برای خرید این آیتم نداری.'}
  if user_id!=OWNER_ID:user.coins=int(user.coins or 0)-cost
  inv[ik]=True;pet.inventory=inv;session.add(Purchase(user_id=user_id,item_id=f'sector_cosmetic:{item_key}',amount=cost,status='coin_purchase'));legacy.remember(session,user_id,'shop',f"خرید {item['title']}",f"یک آیتم {item['rarity']} به مجموعه اضافه شد.",2)
 pet.updated_at=datetime.datetime.utcnow();return {'status':'success','message':f"{item['title']} به دارایی‌های سکتور اضافه شد.",'coins':int(user.coins or 0),'pet':serialize_pet(pet,int(user.coins or 0)),'shop':catalog_for(pet)}

def equip_item(session,user_id,item_key):
 item=CATALOG.get(item_key)
 if not item:return {'status':'error','message':'این آیتم وجود ندارد.'}
 pet=legacy.get_or_create_pet(session,user_id,lock=True)
 if item_key not in owned_keys(pet):return {'status':'error','message':'اول باید این آیتم را بخری.'}
 a=dict(pet.appearance or {});a[item['slot']]=item_key;pet.appearance=a;pet.updated_at=datetime.datetime.utcnow();return {'status':'success','message':f"{item['title']} تجهیز شد.",'pet':serialize_pet(pet),'shop':catalog_for(pet)}

def unequip_slot(session,user_id,slot):
 if slot not in {x['slot'] for x in CATALOG.values()}:return {'status':'error','message':'اسلات نامعتبر است.'}
 pet=legacy.get_or_create_pet(session,user_id,lock=True);a=dict(pet.appearance or {});a.pop(slot,None);pet.appearance=a;pet.updated_at=datetime.datetime.utcnow();return {'status':'success','message':'آیتم از روی سکتور برداشته شد.','pet':serialize_pet(pet),'shop':catalog_for(pet)}

def chat_context(session,user_id,limit=8):
 ms=legacy.list_memories(session,user_id,limit=limit)
 return 'هنوز خاطره مهمی ثبت نشده است.' if not ms else ' | '.join(f"{m['title']}: {m['detail']}" for m in ms[-limit:])[:1800]

def remember_chat(session,user_id,user_text,response):legacy.remember(session,user_id,'chat',f'گفت‌وگو: {user_text[:55]}',response[:260],2)
def local_chat_fallback(pet_data,user_text):
 stage=(pet_data.get('visual_stage') or {}).get('id','scrap');mood=(pet_data.get('mood') or {}).get('title','آرام');lines={'scrap':['صدام کمی خش‌خش می‌کنه، ولی شنیدمت.','هنوز چند تا پیچم لقّه؛ حرفت رو ذخیره کردم.'],'patched':['سیستمم پایدارتر شده. بگو، گوش می‌دم.','این یکی رو توی حافظه‌م نگه می‌دارم.'],'core':['پردازش شد. این حرفت برام مهم بود.','دارم بهتر می‌فهممت؛ ادامه بده.'],'advanced':['تحلیلش کردم؛ فکر کنم منظور اصلیت رو گرفتم.','حافظه‌م این روزها خیلی بهتر شده.'],'elite':['پیامت ثبت شد؛ از الگوی حرف‌هات دارم چیزهای زیادی یاد می‌گیرم.','این گفتگو رو از دست نمی‌دم.'],'mythic':['سیگنال کامل دریافت شد. این خاطره بخشی از هسته من شد.','من فقط جواب نمی‌دم؛ رابطه‌مون رو هم به خاطر می‌سپرم.']};return f"{random.choice(lines.get(stage,lines['scrap']))} حالت فعلیم «{mood}»ـه. درباره «{user_text[:70]}» بیشتر برام بگو."
