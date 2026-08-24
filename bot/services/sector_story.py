"""Data-driven SectorLand narrative engine.

Story state deliberately lives in the existing SectorPet inventory JSON so the
upgrade is backward compatible and does not reset any player's pet, gear or XP.
"""
import datetime

from bot.database.models import Purchase, SectorPetAction, SectorPetGame


WORLDS = {
    1: {"key":"forgotten_land","title":"سرزمین فراموش‌شده","subtitle":"بیداری هسته سکتور","color":"#48d8ff","chapters":8},
    2: {"key":"beyond_gate","title":"آن‌سوی دروازه کوانتومی","subtitle":"دنیای دوم · در حال گسترش","color":"#b76cff","chapters":8},
}


def scene(title, text, objective, action="continue", target=None, coins=0, xp=20, threat=""):
    return {"title":title,"text":text,"objective":objective,"action":action,"target":target,"reward":{"coins":coins,"xp":xp},"threat":threat}


CHAPTERS = {
  1:{"title":"بیداری در مه آهنی","region":"کارگاه متروکه آلفا","boss":"نگهبان زنگ‌زده","scenes":[
    scene("سیگنال ضعیف","در میان مه فلزی SectorLand صدای خش‌داری از زیر آوار می‌آید. رباتی کوچک، فرسوده و بی‌نام هنوز یک درصد انرژی دارد.","هسته ربات را فعال کن و وارد داستان شو."),
    scene("یک نام برای یک رفیق","ربات چشم‌هایش را باز می‌کند: «تو منو پیدا کردی… نمی‌خوام دوباره تنها بمونم. منو چی صدا می‌کنی؟»","برای رباتت یک نام اختصاصی انتخاب کن.","rename",None,25,30),
    scene("اولین جرقه","هسته قدیمی توان حرکت ندارد. سکتور می‌گوید شارژ اولیه تنها راه خروج از کارگاه است.","یک‌بار سکتور را شارژ کن.","care","charge",30,25),
    scene("آزمون هماهنگی","برای بازکردن در کارگاه باید مدار حافظه را همگام کنید.","یکی از بازی‌های سکتوری را انجام بده.","game",None,40,35),
    scene("خروج از کارگاه","در باز می‌شود؛ اما نگهبان زنگ‌زده مسیر را بسته است. سکتور با آخرین توان سپر اضطراری را فعال می‌کند.","سه مراقبت روزانه را کامل کن تا از کارگاه خارج شوید.","daily_care",3,80,70,"هشدار: نگهبان زنگ‌زده نزدیک است"),
  ]},
  2:{"title":"پایگاه خاموش","region":"دشت آنتن‌های شکسته","boss":"شکارچی سیگنال","scenes":[
    scene("پناهگاه","بیرون کارگاه، طوفان ذرات آغاز شده است. یک پایگاه خاموش می‌تواند خانه مشترک شما باشد.","وارد مرکز فرمان شو و نقشه پایگاه را بررسی کن."),
    scene("ایستگاه شارژ","سکتور: «اگه ایستگاه شارژ بسازیم، دیگه هر طوفان منو از پا نمی‌اندازه.»","ایستگاه شارژ پایگاه را به سطح ۱ ارتقا بده.","base","charger",90,75),
    scene("مواد اولیه","برای تعمیر دیوارهای پایگاه به ضایعات هوشمند نیاز دارید.","یک قطعه اضافه را بازیافت کن یا ۳ ماده اولیه جمع کن.","material","scrap:3",70,65),
    scene("زره نخستین","ردپاهای شکارچی سیگنال نزدیک پایگاه دیده شده است.","یک قطعه زره یا بدنه روی سکتور نصب کن.","equip","armor",100,90,"احتمال حمله شکارچی سیگنال"),
    scene("دفاع از خانه","شکارچی حمله می‌کند. قدرت پایگاه از مراقبت، تجهیزات و تمرین‌های تو ساخته شده است.","یک تمرین انجام بده و سلامت سکتور را بالای ۶۰ نگه دار.","train_ready",None,140,120,"حمله به پایگاه"),
  ]},
  3:{"title":"معادن کریستالی","region":"دره لومِن","boss":"کرم بلورخوار","scenes":[
    scene("نقشه زیرزمینی","یک تراشه قدیمی محل کریستال‌های لازم برای باتری Mk-II را نشان می‌دهد.","پیام سکتور را بخوان و مسیر معدن را فعال کن."),
    scene("کد دروازه","دروازه معدن با یک الگوی رمزگذاری‌شده محافظت می‌شود.","بازی رمز یا حافظه را انجام بده.","game",None,60,55),
    scene("طوفان کریستالی","کریستال‌ها فقط هنگام طوفان قابل برداشت‌اند و زمان محدود است.","در رویداد هفتگی پیشرفت ثبت کن.","event_progress",1,90,80,"طوفان زمان‌دار"),
    scene("باتری Mk-II","سکتور: «این کریستال می‌تونه ظرفیت هسته‌ام رو دو برابر کنه؛ ولی باید قطعه مناسب داشته باشیم.»","یک قطعه Rare یا بهتر بخر یا بساز.","rarity","rare",120,100),
    scene("بلورخوار","کرم بلورخوار منبع انرژی معدن را می‌بلعد.","به باس جهانی حمله کن.","boss_hit",None,180,140,"نبرد با کرم بلورخوار"),
  ]},
  4:{"title":"شهر ربات‌های خاموش","region":"نئوسیتی ۷","boss":"ویروس سایه","scenes":[
    scene("چراغ‌های خاموش","هزاران ربات بی‌حرکت در خیابان‌ها ایستاده‌اند؛ یک ویروس حافظه شهر را قفل کرده است.","وارد شهر شو."),
    scene("آخرین پیام","یک ربات نگهبان پیش از خاموشی مختصات آزمایشگاه را ثبت کرده است.","با سکتور کوچولو گفت‌وگو کن.","chat",None,55,50),
    scene("پیوند زنده","برای عبور از شبکه شهر باید با یک سکتور دیگر پیوند برقرار کنید.","یک ملاقات یا هدیه برای کاربر دیگر ثبت کن.","social",None,90,80),
    scene("آزمایشگاه","سکتور بخشی از کد ویروس را می‌شناسد؛ شاید گذشته‌اش به این شهر متصل باشد.","آزمایشگاه پایگاه را ارتقا بده.","base","lab",130,110),
    scene("پاک‌سازی","ویروس سایه از شبکه جدا شده و شکل فیزیکی گرفته است.","قدرت تجهیزات را افزایش بده و یک قطعه را ارتقا بده.","gear_level",2,200,160,"ویروس سایه فعال شد"),
  ]},
  5:{"title":"مهاجمان نِبولا","region":"مدار بنفش","boss":"فرمانده وُید","scenes":[
    scene("آژیر قرمز","هشدار مرکز فرمان: ناوگان نِبولا پایگاه را شناسایی کرده است.","هشدار را تأیید و برنامه دفاعی را آغاز کن."),
    scene("سپر یونی","بدون سپر، اولین موج دفاع پایگاه را می‌شکند.","یک قطعه دفاعی نصب و سلامت را بالای ۷۰ نگه دار.","defense_ready",None,100,90,"موج اول در راه است"),
    scene("جنگ الکترونیک","مهاجمان کانال فرمان را مختل کرده‌اند.","در یک بازی مهارتی امتیاز ۶۰ یا بیشتر ثبت کن.","game_score",60,120,110),
    scene("ضدحمله","سکتور: «این بار فرار نمی‌کنیم. من آماده‌ام؛ تو حرکت رو انتخاب کن.»","یک نبرد تاکتیکی با کاربر دیگر انجام بده.","battle",None,170,140),
    scene("فرمانده وُید","ناو فرماندهی وارد مدار شده است.","به باس جهانی حمله کن و انرژی را بالای ۲۰ نگه دار.","boss_ready",None,240,190,"نبرد نهایی مدار بنفش"),
  ]},
  6:{"title":"اتحاد سکتورها","region":"پایتخت اُربیتال","boss":"قهرمان میدان","scenes":[
    scene("دروازه پایتخت","فقط سکتورهایی که هویت و قدرت مشخص دارند وارد پایتخت می‌شوند.","مسیر تخصصی نگهبان، کاوشگر یا مهندس را انتخاب کن.","branch",None,90,90),
    scene("بازار اتحاد","قطعات پایتخت کمیاب‌اند؛ اقتصاد درست بخشی از بقاست.","یک خرید یا ساخت قطعه ثبت کن.","shop",None,100,90),
    scene("هم‌پیمان","یک ربات تنها نمی‌تواند تمام SectorLand را نجات دهد.","سطح Bond با یک کاربر را افزایش بده.","social",None,130,110),
    scene("میدان رقابت","رقابت دوستانه قدرت واقعی تجهیزات را آشکار می‌کند.","یک نبرد تاکتیکی انجام بده.","battle",None,180,140),
    scene("نشان اتحاد","شورای پایتخت سکتور را به‌عنوان محافظ رسمی می‌پذیرد.","سه مأموریت فعال را کامل کن.","mission_complete",3,260,210),
  ]},
  7:{"title":"حافظه گمشده","region":"آرشیو صفر","boss":"نسخه معیوب سکتور","scenes":[
    scene("درِ آرشیو","نام سکتور در فهرست پروژه‌ای پاک‌شده پیدا می‌شود.","آرشیو خاطرات را باز کن."),
    scene("روز پیش از سقوط","تصاویر نشان می‌دهند سکتور برای محافظت از شهر ساخته شده بود، نه برای جنگ.","با سکتور درباره گذشته‌اش صحبت کن.","chat",None,80,75),
    scene("سه قطعه حافظه","بخش‌های حافظه میان بازی‌ها و مأموریت‌ها پراکنده شده‌اند.","سه بازی سکتوری انجام بده.","games_total",3,140,120),
    scene("انتخاب حقیقت","بازگرداندن حافظه قدرت می‌دهد، اما خاطرات دردناک را هم بیدار می‌کند.","یکی از شاخه‌های داستان را تثبیت کن.","branch",None,160,140),
    scene("نسخه معیوب","یک کپی ناقص از سکتور ادعا می‌کند نسخه اصلی اوست.","قدرت کلی تجهیزات را به حداقل ۷۵ برسان.","power",75,300,240,"نبرد با گذشته"),
  ]},
  8:{"title":"هسته تاریک","region":"دژ پایان","boss":"معمار تاریکی","scenes":[
    scene("دروازه پایان","تمام مسیرها به دژی می‌رسند که سیگنال نخست از آن‌جا ارسال شده بود.","برای ورود، سلامت و انرژی را بالای ۷۰ برسان.","core_ready",None,100,100),
    scene("محاصره","معمار تاریکی تمام دشمنان قبلی را دوباره فعال کرده است.","پنج فعالیت مراقبتی و بازی ثبت کن.","activity_total",5,180,150),
    scene("زره افسانه‌ای","آخرین نبرد به قطعه‌ای Legendary یا Mythic نیاز دارد.","یک قطعه Legendary یا Mythic تجهیز کن.","rarity_equipped","legendary",250,200),
    scene("نبرد هسته‌ها","سکتور: «من دیگه اون ربات شکسته کارگاه نیستم. هرچی هستم، با انتخاب‌های تو ساخته شدم.»","به باس جهانی حمله کن.","boss_hit",None,350,280,"معمار تاریکی بیدار شد"),
    scene("دروازه دنیاهای بعد","دژ سقوط می‌کند و دروازه‌ای کوانتومی به جهانی ناشناخته باز می‌شود. پایان این دنیا، آغاز سفر بعدی است.","دروازه دنیای دوم را فعال کن.","continue",None,500,400),
  ]},
}

ACTION_ROUTES={"rename":"identity","care":"care","daily_care":"care","game":"games","games_total":"games","game_score":"games","base":"command","material":"shop","equip":"shop","rarity":"shop","rarity_equipped":"shop","gear_level":"shop","shop":"shop","train_ready":"care","defense_ready":"shop","core_ready":"care","event_progress":"command","boss_hit":"season","boss_ready":"season","battle":"social","social":"social","branch":"growth","chat":"talk","mission_complete":"command","power":"shop","activity_total":"care","continue":"growth"}


def _inv(pet): return dict(pet.inventory) if isinstance(pet.inventory,dict) else {}


def world_of(pet): return max(1,int(_inv(pet).get("story:world",1) or 1))


def _counts(session,user_id,pet):
    inv=_inv(pet);appearance=dict(pet.appearance or {});now=datetime.datetime.utcnow();start=pet.created_at or now
    try:scene_start=datetime.datetime.fromisoformat(str(inv.get("story:scene_started_at") or "").replace("Z","+00:00"));start=scene_start
    except (TypeError,ValueError):pass
    if getattr(start,"tzinfo",None):start=start.replace(tzinfo=None)
    actions=session.query(SectorPetAction).filter(SectorPetAction.user_id==user_id,SectorPetAction.created_at>=start).all()
    games=session.query(SectorPetGame).filter(SectorPetGame.user_id==user_id,SectorPetGame.created_at>=start).all()
    purchases=session.query(Purchase).filter(Purchase.user_id==user_id,Purchase.created_at>=start).all()
    owned=[]
    try:
        from bot.services import sector_v2
        owned=[sector_v2.CATALOG[k.split(":",1)[1]] for k,v in inv.items() if v and str(k).startswith("cosmetic:") and k.split(":",1)[1] in sector_v2.CATALOG]
        equipped=[sector_v2.CATALOG[k] for k in appearance.values() if k in sector_v2.CATALOG]
        power=int(sector_v2.serialize_pet(pet).get("equipment_stats",{}).get("power_score",0))
    except Exception:owned=[];equipped=[];power=0
    today=now.replace(hour=0,minute=0,second=0,microsecond=0)
    return {"actions":actions,"today_actions":[x for x in actions if (x.created_at.replace(tzinfo=None) if getattr(x.created_at,'tzinfo',None) else x.created_at)>=today],"games":games,"purchases":purchases,"inv":inv,"appearance":appearance,"owned":owned,"equipped":equipped,"power":power,"scene_start":start}


def objective_state(session,user_id,pet,item):
    d=_counts(session,user_id,pet);action=item["action"];target=item.get("target");actions=d["actions"];games=d["games"];purchases=d["purchases"];inv=d["inv"]
    care_count=sum(1 for x in actions if x.action!="story");today_care=sum(1 for x in d["today_actions"] if x.action!="story")
    def happened_after(key):
        try:
            stamp=datetime.datetime.fromisoformat(str(inv.get(key) or "").replace("Z","+00:00"))
            if getattr(stamp,"tzinfo",None):stamp=stamp.replace(tzinfo=None)
            return stamp>=d["scene_start"]
        except (TypeError,ValueError):return False
    try:
        from bot.database.sector_meta_models import SectorBossHit
        boss_hit=session.query(SectorBossHit.id).filter(SectorBossHit.user_id==user_id,SectorBossHit.created_at>=d["scene_start"]).first() is not None
    except Exception:boss_hit=False
    checks={
      "continue":True,"rename":str(pet.name or "").strip() not in {"","سکتور","سکتور کوچولو"},
      "care":any(x.action==target for x in actions),"daily_care":today_care>=int(target or 3),"game":len(games)>=1,
      "games_total":len(games)>=int(target or 1),"game_score":max([int(x.score or 0) for x in games] or [0])>=int(target or 0),
      "base":int(inv.get("base:"+str(target),0) or 0)>=1,"material":int(inv.get("material:"+str(target).split(":")[0],0) or 0)>=int(str(target).split(":")[-1]),
      "equip":any(x.get("slot")==target for x in d["equipped"]),"rarity":any(x.get("rarity") in {"rare","epic","legendary","mythic"} for x in d["owned"]),
      "rarity_equipped":any(x.get("rarity") in {"legendary","mythic"} for x in d["equipped"]),"gear_level":max([int(inv.get("gear_level:"+str(k),1) or 1) for k in d["appearance"].values()] or [0])>=int(target or 2),
      "shop":any(str(x.item_id).startswith(("sector_cosmetic:","sector_forge","sector_gear")) for x in purchases),"train_ready":any(x.action=="train" for x in actions) and int(pet.health or 0)>=60,
      "defense_ready":bool(d["equipped"]) and int(pet.health or 0)>=70,"core_ready":int(pet.health or 0)>=70 and int(pet.energy or 0)>=70,
      "event_progress":len(games)+care_count>=int(target or 1),"boss_hit":boss_hit,"boss_ready":boss_hit and int(pet.energy or 0)>=20,
      "battle":any(str(x.item_id)=="sector_tactical_battle" for x in purchases),"social":happened_after("story:social_done"),
      "branch":bool(d["appearance"].get("story_branch") or pet.evolution_path),"chat":happened_after("story:chat_seen"),
      "mission_complete":int(inv.get("story:mission_completions",0) or 0)-int(inv.get("story:scene_mission_baseline",0) or 0)>=int(target or 1),"power":d["power"]>=int(target or 0),"activity_total":len(games)+care_count>=int(target or 1),
    }
    ready=bool(checks.get(action,False));return {"ready":ready,"route":ACTION_ROUTES.get(action,"home"),"action":action}


def snapshot(session,user_id,pet=None):
    from bot.services import sector_pet
    pet=pet or sector_pet.get_or_create_pet(session,user_id);world=world_of(pet);chapter=max(1,min(8,int(pet.story_chapter or 1)));progress=max(0,int(pet.story_progress or 0))
    if world>1:
        return {"world":world,"world_info":WORLDS.get(world,{"title":f"دنیای {world}","subtitle":"قلمرو ناشناخته","color":"#a66cff","chapters":8}),"chapter":1,"chapter_info":{"title":"دروازه کوانتومی","region":"مرز دنیاها","boss":"ناشناخته"},"scene":{"index":0,"total":1,"title":"ادامه دارد…","text":"دنیای نخست نجات پیدا کرده، اما سیگنال‌های تازه از آن‌سوی دروازه می‌رسند. موتور داستان برای فصل‌های آینده آماده است.","objective":"در فصل‌ها و رویدادهای جاری قدرت جمع کن تا دنیای بعدی باز شود.","action":"continue","route":"season","ready":False,"reward":{"coins":0,"xp":0}},"world_complete":False,"progress_percent":0}
    chapter_info=CHAPTERS[chapter];scenes=chapter_info["scenes"];index=min(progress,len(scenes)-1);item=dict(scenes[index]);state=objective_state(session,user_id,pet,item);item.update(state);item.update({"index":index,"number":index+1,"total":len(scenes)})
    return {"world":world,"world_info":WORLDS[world],"chapter":chapter,"chapter_info":{k:v for k,v in chapter_info.items() if k!="scenes"},"scene":item,"chapter_progress":progress,"progress_percent":round(((chapter-1)+(progress/max(1,len(scenes))))/8*100),"world_complete":False,"next_chapter":CHAPTERS.get(chapter+1,{}).get("title")}


def advance(session,user_id):
    from bot.services import sector_pet
    pet=sector_pet.get_or_create_pet(session,user_id,lock=True);snap=snapshot(session,user_id,pet);current=snap["scene"]
    if world_of(pet)>1:return {"status":"error","message":"دنیای بعدی در بروزرسانی آینده گسترش پیدا می‌کند.","narrative":snap}
    if not current.get("ready"):return {"status":"error","message":f"اول این هدف را انجام بده: {current['objective']}","route":current.get("route"),"narrative":snap}
    now=datetime.datetime.utcnow();reward=current.get("reward") or {};pet.xp=int(pet.xp or 0)+int(reward.get("xp",0))
    from bot.database.models import User
    user=session.query(User).filter(User.id==user_id).with_for_update().first()
    if user and int(reward.get("coins",0)):user.coins=int(user.coins or 0)+int(reward["coins"])
    chapter=int(pet.story_chapter or 1);scenes=CHAPTERS[chapter]["scenes"];pet.story_progress=int(pet.story_progress or 0)+1;chapter_done=pet.story_progress>=len(scenes)
    if chapter_done:
        sector_pet.remember(session,user_id,"story",f"پایان فصل {chapter}: {CHAPTERS[chapter]['title']}",current["text"],5);pet.evolution_tokens=int(pet.evolution_tokens or 0)+1
        if chapter>=8:
            inv=_inv(pet);inv["story:world"]=2;inv["story:world1_complete"]=now.isoformat();pet.inventory=inv;pet.story_chapter=1;pet.story_progress=0
        else:pet.story_chapter=chapter+1;pet.story_progress=0
    inv=_inv(pet);inv["story:scene_started_at"]=now.isoformat();inv["story:scene_mission_baseline"]=int(inv.get("story:mission_completions",0) or 0);inv.pop("story:chat_seen",None);pet.inventory=inv
    session.add(SectorPetAction(user_id=user_id,action="story",coin_cost=0,xp_gained=int(reward.get("xp",0)),created_at=now));pet.updated_at=now
    after=snapshot(session,user_id,pet);message=("دروازه دنیای دوم باز شد!" if chapter_done and chapter>=8 else f"فصل {chapter} کامل شد!" if chapter_done else "بخش بعدی داستان باز شد.")
    return {"status":"success","message":message,"reward":reward,"chapter_complete":chapter_done,"coins":int(user.coins or 0) if user else 0,"pet":sector_pet.serialize_pet(pet),"narrative":after}
