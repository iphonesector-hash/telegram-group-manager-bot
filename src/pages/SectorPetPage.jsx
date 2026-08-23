import { useEffect, useMemo, useState } from 'react'
import { useAppContext } from '../App'
import SectorCelebration from '../components/ui/SectorCelebration'

const ICONS={charge:'⚡',play:'🎮',train:'🏋️',learn:'🧠',repair:'🔧',feed:'🍪',clean:'🫧',sleep:'🌙'}
const STATS={energy:['⚡','انرژی'],happiness:['💙','شادی'],hunger:['🍪','سیری'],cleanliness:['🫧','نظافت'],knowledge:['🧠','دانش'],health:['❤️','سلامتی']}
const ITEMS={neon_lamp:{title:'چراغ نئونی',icon:'💡',cost:450},game_console:{title:'کنسول بازی',icon:'🕹️',cost:900},space_window:{title:'پنجره فضایی',icon:'🪐',cost:1800},ai_core:{title:'هسته هوشمند',icon:'🔮',cost:4000}}
const MILESTONES=[3,7,14,30]

function Meter({name,value}){
  var meta=STATS[name]
  return <div style={{marginBottom:10}}><div style={{display:'flex',justifyContent:'space-between',fontSize:11,marginBottom:5}}><span>{meta[0]} {meta[1]}</span><b>{value}%</b></div><div className="progress-bar"><div className="progress-fill" style={{width:value+'%',background:value<25?'linear-gradient(90deg,#ff5578,#ff8d54)':undefined}}/></div></div>
}

function streakMeta(days){
  var d=Number(days||0)
  var next=MILESTONES.find(function(x){return x>d})||30
  var prev=[0].concat(MILESTONES).filter(function(x){return x<=d}).pop()||0
  var pct=next===prev?100:Math.max(0,Math.min(100,Math.round((d-prev)/Math.max(1,next-prev)*100)))
  var label=d>=30?'افسانه‌ای':d>=14?'حرفه‌ای':d>=7?'پایدار':d>=3?'گرم‌شده':'در حال شروع'
  return {next:next,prev:prev,pct:pct,label:label}
}

function moodTheme(mood){
  var title=((mood&&mood.title)||'').toLowerCase()
  if(title.includes('خوش')||title.includes('شاد')||title.includes('هیجان'))return {glow:'rgba(66,231,184,.38)',accent:'#54f2c0'}
  if(title.includes('خواب')||title.includes('آرام'))return {glow:'rgba(110,126,255,.36)',accent:'#8ea2ff'}
  if(title.includes('ناراحت')||title.includes('خسته'))return {glow:'rgba(255,151,92,.34)',accent:'#ffb079'}
  if(title.includes('عصب'))return {glow:'rgba(255,79,106,.34)',accent:'#ff718a'}
  return {glow:'rgba(107,94,241,.38)',accent:'#78e9ff'}
}

function MemoryGame({finish}){
  var symbols=['⚡','🔧','💎','🧠'],[seq,setSeq]=useState([]),[input,setInput]=useState([]),[show,setShow]=useState(false),[playing,setPlaying]=useState(false)
  function start(){var s=Array.from({length:4},function(){return symbols[Math.floor(Math.random()*symbols.length)]});setSeq(s);setInput([]);setPlaying(true);setShow(true);setTimeout(function(){setShow(false)},2200)}
  function tap(x){if(!playing||show)return;var next=input.concat(x);setInput(next);if(x!==seq[next.length-1]){finish('circuit',Math.max(10,(next.length-1)*25));setPlaying(false)}else if(next.length===seq.length){finish('circuit',100);setPlaying(false)}}
  return <div className="glass" style={{padding:14}}><b>🧩 مدار حافظه</b><p style={{fontSize:10,color:'var(--muted)',lineHeight:1.8}}>ترتیب مدارها را به خاطر بسپار و تکرار کن.</p><div style={{minHeight:42,textAlign:'center',fontSize:27,letterSpacing:6}}>{show?seq.join(' '):(playing?'❔ ❔ ❔ ❔':'برای شروع آماده‌ای؟')}</div><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:7,marginTop:9}}>{symbols.map(function(x){return <button key={x} className="btn" disabled={!playing||show} onClick={function(){tap(x)}}>{x}</button>})}</div><button className="btn btn-primary" style={{width:'100%',marginTop:9}} onClick={start}>شروع مدار</button></div>
}

function BatteryGame({finish}){
  var [left,setLeft]=useState(0),[hits,setHits]=useState(0),[running,setRunning]=useState(false)
  useEffect(function(){if(!running)return;if(left<=0){finish('battery',Math.min(100,hits*5));setRunning(false);return}var timer=setTimeout(function(){setLeft(function(v){return v-1})},1000);return function(){clearTimeout(timer)}},[left,running])
  return <div className="glass" style={{padding:14}}><b>🔋 شارژ سریع</b><p style={{fontSize:10,color:'var(--muted)',lineHeight:1.8}}>در ۱۰ ثانیه هسته انرژی را تا می‌توانی لمس کن.</p><div style={{fontSize:12,textAlign:'center'}}>زمان: {left} • شارژ: {hits}</div><button className="btn btn-gold" disabled={!running} onClick={function(){setHits(function(v){return v+1})}} style={{width:'100%',height:82,fontSize:35,marginTop:9}}>⚡</button><button className="btn btn-primary" disabled={running} onClick={function(){setHits(0);setLeft(10);setRunning(true)}} style={{width:'100%',marginTop:9}}>شروع شارژ</button></div>
}

export default function SectorPetPage(){
  var ctx=useAppContext(),user=ctx.tgUser
  var [data,setData]=useState(null),[tab,setTab]=useState('home'),[busy,setBusy]=useState(''),[newName,setNewName]=useState(''),[message,setMessage]=useState(''),[chat,setChat]=useState([]),[target,setTarget]=useState(''),[clanName,setClanName]=useState(''),[leaderboard,setLeaderboard]=useState([]),[admin,setAdmin]=useState(null),[eventTitle,setEventTitle]=useState(''),[giftAmount,setGiftAmount]=useState(100),[celebration,setCelebration]=useState(null)

  function load(){
    if(!user)return
    ctx.apiCall('getSectorPet',user.id).then(function(r){if(r&&r.data)setData(r.data)})
    if(ctx.dbUser.is_admin)ctx.apiCall('getSectorAdmin',user.id).then(function(r){if(r&&r.data){setAdmin(r.data);setEventTitle((r.data.event||{}).title||'')}})
  }
  useEffect(load,[user,ctx.apiCall])

  function applyResult(d){
    if(d&&d.status==='success'){
      var previous=data&&data.pet?data.pet:{}
      var next=d.pet||previous
      var oldLevel=Number(previous.level||1),newLevel=Number(next.level||oldLevel)
      var oldStreak=Number(previous.streak_days||0),newStreak=Number(next.streak_days||oldStreak)
      setData(function(v){return {...v,pet:next,daily:d.daily||(v&&v.daily)}})
      if(d.coins!==undefined)ctx.setDbUser(function(u){return {...u,coins:Number(d.coins)}})
      ctx.showToast(d.message,'success')
      if(newLevel>oldLevel){
        setCelebration({title:'LEVEL UP! 🚀',text:'سکتور کوچولو به سطح '+newLevel+' رسید. رشدش ثبت شد و مسیرهای جدید نزدیک‌تر شدند.'})
      }else if(MILESTONES.indexOf(newStreak)>=0&&newStreak>oldStreak){
        setCelebration({title:'🔥 زنجیره '+newStreak+' روزه!',text:'یک Milestone واقعی باز کردی. ادامه بده تا پاداش و تکامل‌های بعدی سریع‌تر آزاد شوند.'})
      }
    }else ctx.showToast((d&&d.message)||'عملیات انجام نشد.','error')
  }
  function act(id){if(busy)return;setBusy(id);ctx.apiCall('sectorPetAction',user.id,id).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function buy(id){if(busy)return;setBusy('buy');ctx.apiCall('buySectorRoomItem',user.id,id).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function finish(game,score){if(busy)return;setBusy('game');ctx.apiCall('finishSectorGame',user.id,game,score).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function evolve(key){setBusy('evolve');ctx.apiCall('chooseSectorEvolution',user.id,key).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function cosmetic(key){setBusy('cosmetic');ctx.apiCall('buySectorCosmetic',user.id,key).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function story(){setBusy('story');ctx.apiCall('advanceSectorStory',user.id).then(function(r){applyResult(r&&r.data);setBusy('');load()})}
  function job(key){setBusy('job');ctx.apiCall('sectorJob',user.id,key).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function social(action){if(!target.trim())return ctx.showToast('نام کاربری مقصد را وارد کن','error');setBusy('social');ctx.apiCall('sectorSocial',user.id,action,target).then(function(r){applyResult(r&&r.data);setBusy('')})}
  function clan(action){if(!clanName.trim())return ctx.showToast('نام تیم را وارد کن','error');setBusy('clan');ctx.apiCall('sectorClan',user.id,action,clanName).then(function(r){var d=r&&r.data;if(d&&d.status==='success'){setData(function(v){return {...v,clan:d.clan}});ctx.showToast(d.message,'success')}else ctx.showToast((d&&d.message)||'عملیات تیم انجام نشد','error');setBusy('')})}
  function showLeaders(){ctx.apiCall('getSectorLeaderboard').then(function(r){if(r&&r.data)setLeaderboard(r.data)})}
  function saveEvent(){setBusy('admin');ctx.apiCall('updateSectorAdmin',user.id,{title:eventTitle,reward:(admin&&admin.event&&admin.event.reward)||100,active:true}).then(function(r){var d=r&&r.data;if(d&&d.status==='success'){setAdmin(function(v){return {...v,event:d.event}});ctx.showToast(d.message,'success')}setBusy('')})}
  function sendGift(){if(!window.confirm('هدیه برای تمام صاحبان سکتور ارسال شود؟'))return;setBusy('gift');ctx.apiCall('sendSectorGift',user.id,Number(giftAmount)).then(function(r){var d=r&&r.data;ctx.showToast((d&&d.message)||'هدیه ارسال نشد',d&&d.status==='success'?'success':'error');setBusy('')})}
  function rename(){var name=newName.trim();if(!name)return;setBusy('rename');ctx.apiCall('renameSectorPet',user.id,name).then(function(r){applyResult(r&&r.data);setNewName('');setBusy('')})}
  function talk(){var text=message.trim();if(!text||busy)return;setMessage('');setChat(function(v){return v.concat({role:'user',text:text})});setBusy('talk');ctx.apiCall('talkSectorPet',user.id,text).then(function(r){var d=r&&r.data;if(d&&d.status==='success')setChat(function(v){return v.concat({role:'pet',text:d.response})});else ctx.showToast((r&&r.error)||'سکتور جواب نداد','error');setBusy('')})}

  var tabs=useMemo(function(){return [['home','🏠 خانه'],['care','💙 مراقبت'],['journey','🧬 مسیر'],['closet','🎨 کمد'],['games','🎮 بازی'],['social','🤝 اجتماع'],['memories','📔 خاطرات'],['talk','💬 گفتگو']]},[])
  if(!data)return <div className="page"><div className="glass" style={{padding:24,textAlign:'center'}}>🤖 در حال بیدار کردن سکتور...</div></div>

  var pet=data.pet,stage=pet.stage||{id:1,title:'سکتور کوچولو'},daily=data.daily||{goals:[]},mood=pet.mood||{emoji:'🤖',title:'آرام',line:'خوشحالم که برگشتی.'},owned=pet.inventory||{}
  var streak=streakMeta(pet.streak_days),theme=moodTheme(mood)
  var roomItems=Object.keys(owned)

  function toggleNotifications(){ctx.apiCall('setSectorNotifications',user.id,!pet.notifications_enabled).then(function(r){applyResult(r&&r.data)})}

  return <div className="page fade-up">
    <SectorCelebration open={!!celebration} title={celebration&&celebration.title} text={celebration&&celebration.text} onClose={function(){setCelebration(null)}}/>

    <div className="glass" style={{padding:0,textAlign:'center',overflow:'hidden',border:'1px solid rgba(110,94,241,.32)',background:'linear-gradient(160deg,rgba(35,22,91,.92),rgba(6,12,28,.98))'}}>
      <div style={{position:'relative',height:245,overflow:'hidden'}}>
        <img src="/assets/sector/mascot-emotions.webp" alt="سکتور کوچولو" style={{width:'150%',maxWidth:'none',position:'absolute',left:'50%',top:'48%',transform:'translate(-50%,-50%)',filter:'drop-shadow(0 20px 42px '+theme.glow+')'}}/>
        <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,rgba(4,8,24,.12),rgba(4,8,24,.15) 48%,rgba(6,12,28,.96) 100%)'}}/>
        <div style={{position:'absolute',top:12,left:12,right:12,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <span style={{fontSize:10,color:'#7ff7ff',fontWeight:900,letterSpacing:1}}>SECTOR COMPANION</span>
          <span style={{fontSize:10,padding:'5px 8px',borderRadius:10,background:'rgba(0,0,0,.34)',border:'1px solid rgba(255,255,255,.1)'}}>Lv.{pet.level}</span>
        </div>
        <div style={{position:'absolute',left:12,right:12,bottom:12,textAlign:'right'}}>
          <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:29}}>{mood.emoji}</span><div><b style={{fontSize:21}}>{pet.name}</b><div style={{fontSize:10,color:'var(--muted)'}}>{stage.title} • شخصیت {pet.personality}</div></div></div>
          <div style={{marginTop:7,padding:'8px 10px',borderRadius:12,background:'rgba(5,10,25,.72)',border:'1px solid rgba(255,255,255,.08)',fontSize:11}}><b style={{color:theme.accent}}>{mood.title}:</b> {mood.line}</div>
        </div>
      </div>
      <div style={{padding:'4px 15px 15px'}}><div style={{display:'flex',justifyContent:'space-between',fontSize:10,color:'var(--muted)'}}><span>XP سطح</span><span>{pet.xp_in_level} / {pet.xp_next}</span></div><div className="progress-bar" style={{marginTop:6}}><div className="progress-fill" style={{width:Math.min(100,pet.xp_in_level/Math.max(1,pet.xp_next)*100)+'%'}}/></div></div>
    </div>

    <div className="glass" style={{display:'flex',gap:4,padding:5,margin:'10px 0 14px',position:'sticky',top:5,zIndex:5,overflowX:'auto'}}>{tabs.concat(ctx.dbUser.is_admin?[['command','👑 فرمانده']]:[]).map(function(t){return <button key={t[0]} onClick={function(){setTab(t[0])}} style={{flex:'0 0 auto',border:0,borderRadius:10,padding:'9px 10px',fontSize:10,color:'white',background:tab===t[0]?'linear-gradient(135deg,#4169ff,#8a43ff)':'transparent'}}>{t[1]}</button>})}</div>

    {tab==='home'&&<>
      <div className="glass" style={{padding:14,marginBottom:10,background:'linear-gradient(135deg,rgba(255,123,55,.11),rgba(115,65,255,.11))'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:10}}><div><b>🔥 زنجیره حضور: {pet.streak_days||0} روز</b><div style={{fontSize:10,color:'var(--muted)',marginTop:3}}>وضعیت: {streak.label}</div></div><div style={{fontWeight:900,color:'var(--gold)'}}>{Number(pet.total_care_days||0).toLocaleString('fa-IR')} روز مراقبت</div></div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:9,color:'var(--muted)',marginTop:10}}><span>Milestone قبلی {streak.prev}</span><span>هدف بعدی {streak.next} روز</span></div>
        <div className="progress-bar" style={{marginTop:5}}><div className="progress-fill" style={{width:streak.pct+'%',background:'linear-gradient(90deg,#ff9f43,#7b5cff)'}}/></div>
        <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:6,marginTop:10}}>{MILESTONES.map(function(m){var done=Number(pet.streak_days||0)>=m;return <div key={m} style={{padding:'7px 4px',borderRadius:10,textAlign:'center',fontSize:9,border:'1px solid '+(done?'rgba(255,190,70,.35)':'var(--border)'),background:done?'rgba(255,180,60,.1)':'rgba(255,255,255,.025)'}}><div style={{fontSize:17}}>{done?'🔥':'○'}</div>{m} روز</div>})}</div>
      </div>

      <div className="sec-title">ماموریت‌های امروز</div><div className="glass" style={{padding:14}}>{(daily.goals||[]).map(function(g){return <div key={g.id} style={{display:'flex',justifyContent:'space-between',fontSize:11,padding:'7px 0',borderBottom:'1px solid var(--border)'}}><span>{g.complete?'✅':'🔄'} {g.title}</span><b>{g.progress}/{g.target}</b></div>})}</div>

      <div className="sec-title">نشان‌های من</div><div className="glass" style={{padding:12,overflow:'hidden'}}><img src="/assets/sector/rank-badges.webp" alt="نشان‌های Sector" loading="lazy" style={{width:'100%',display:'block',borderRadius:10,marginBottom:10}}/><div style={{display:'flex',gap:8,overflowX:'auto'}}>{(data.achievements||[]).length?(data.achievements||[]).map(function(a){return <div key={a.id} style={{minWidth:80,textAlign:'center'}}><div style={{fontSize:25}}>{a.icon}</div><small>{a.title}</small></div>}):<small style={{color:'var(--muted)'}}>اولین نشان با ۷ روز مراقبت آزاد می‌شود.</small>}</div></div>

      <div className="sec-title">اتاق {pet.name}</div><div className="glass" style={{padding:0,overflow:'hidden',background:'linear-gradient(160deg,rgba(32,51,91,.9),rgba(24,13,57,.96))'}}><div style={{position:'relative',minHeight:180,padding:14,background:'radial-gradient(circle at 50% 20%,rgba(86,69,213,.24),transparent 58%)'}}><img src="/assets/sector/brand-hero.webp" alt="اتاق سکتور" loading="lazy" style={{position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover',opacity:.16}}/><div style={{position:'relative',fontSize:44,textAlign:'center',padding:'36px 8px 16px'}}>{roomItems.length?roomItems.map(function(k){return <span key={k} style={{margin:6}}>{ITEMS[k]&&ITEMS[k].icon}</span>}):'🛏️ 🤖'}</div><div style={{position:'relative',textAlign:'center',fontSize:10,color:'var(--muted)'}}>{roomItems.length?roomItems.length+' آیتم فعال در اتاق':'اتاقت هنوز ساده است؛ اولین آیتم را اضافه کن.'}</div></div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:7,padding:12}}>{Object.entries(ITEMS).map(function(entry){var id=entry[0],it=entry[1];return <button key={id} className="btn" disabled={busy==='buy'||owned[id]} onClick={function(){buy(id)}} style={{fontSize:10}}>{it.icon} {owned[id]?'خریده شد':it.title+' • '+it.cost}</button>})}</div></div>
    </>}

    {tab==='care'&&<>
      <div className="glass" style={{padding:0,overflow:'hidden',marginBottom:12}}><img src="/assets/sector/mascot-emotions.webp" alt="واکنش‌های سکتور" loading="lazy" style={{display:'block',width:'100%'}}/><div style={{padding:'9px 12px',fontSize:10,color:'var(--muted)'}}>هر مراقبت روی Mood، XP و وضعیت واقعی سکتور اثر می‌گذارد.</div></div>
      <div className="sec-title">وضعیت زنده</div><div className="glass" style={{padding:14}}>{Object.keys(STATS).map(function(k){return <Meter key={k} name={k} value={Number(pet[k]||0)}/>})}</div>
      <div className="sec-title">مراقبت و رشد</div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9}}>{(data.actions||[]).map(function(a){return <button key={a.id} className="glass" disabled={!!busy} onClick={function(){act(a.id)}} style={{padding:14,color:'inherit',border:'1px solid var(--border)'}}><div style={{fontSize:27}}>{busy===a.id?'⏳':ICONS[a.id]}</div><b style={{fontSize:11}}>{a.title}</b><div style={{fontSize:9,color:'var(--muted)'}}>{ctx.dbUser.unlimited_wallet?'رایگان':a.cost+' سکه'} • +{a.xp} XP</div></button>})}</div>
      <div className="glass" style={{padding:14,marginTop:12}}><b>✏️ تغییر نام</b><div style={{display:'flex',gap:7,marginTop:8}}><input value={newName} maxLength={20} onChange={function(e){setNewName(e.target.value)}} placeholder={pet.name} style={{flex:1,minWidth:0,padding:10,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'white'}}/><button className="btn btn-primary" onClick={rename}>ثبت</button></div></div>
    </>}

    {tab==='journey'&&<><div className="glass" style={{padding:15}}><b>📖 فصل {pet.story_chapter}: {(data.story||{}).title}</b><p style={{fontSize:11,color:'var(--muted)',lineHeight:1.9}}>{(data.story||{}).text}</p><div className="progress-bar"><div className="progress-fill" style={{width:Math.min(100,pet.story_progress/Math.max(1,(data.story||{}).target)*100)+'%'}}/></div><div style={{fontSize:10,marginTop:6}}>{pet.story_progress}/{(data.story||{}).target} مرحله</div><button className="btn btn-primary" disabled={busy==='story'} onClick={story} style={{width:'100%',marginTop:10}}>🚀 ادامه داستان</button></div><div className="sec-title">مسیر تکامل دائمی</div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>{Object.entries(data.evolution_paths||{}).map(function(entry){var key=entry[0],p=entry[1];return <button key={key} className="glass" disabled={!!pet.evolution_path||busy==='evolve'} onClick={function(){evolve(key)}} style={{padding:13,color:'inherit',border:pet.evolution_path===key?'1px solid #38e6a0':'1px solid var(--border)'}}><div style={{fontSize:25}}>{p.icon}</div><b>{p.title}</b><div style={{fontSize:9,color:'var(--muted)',lineHeight:1.6}}>{p.perk}<br/>از سطح {p.level}</div></button>})}</div><div className="sec-title">شغل سکتور</div>{pet.job?<button className="btn btn-gold" onClick={function(){job('claim')}} style={{width:'100%'}}>🎁 پایان کار و دریافت درآمد</button>:<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>{Object.entries(data.jobs||{}).map(function(entry){var key=entry[0],j=entry[1];return <button key={key} className="btn" onClick={function(){job(key)}}>{j.icon} {j.title}<small style={{display:'block'}}>{j.hours} ساعت • {j.reward} سکه</small></button>})}</div>}</>}

    {tab==='closet'&&<><div className="glass" style={{padding:16,textAlign:'center',overflow:'hidden'}}><img src="/assets/sector/mascot-emotions.webp" alt="ظاهر سکتور" loading="lazy" style={{width:'100%',display:'block',borderRadius:12,marginBottom:10}}/><div style={{fontSize:38}}>{Object.values(pet.appearance||{}).map(function(k){return <span key={k}>{(data.cosmetics||{})[k]&&data.cosmetics[k].icon}</span>})} 🤖</div><div style={{fontSize:10,color:'var(--muted)'}}>ظاهر فعلی {pet.name}</div></div><div className="sec-title">لباس و تجهیزات</div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>{Object.entries(data.cosmetics||{}).map(function(entry){var key=entry[0],it=entry[1];return <button key={key} className="glass" disabled={busy==='cosmetic'} onClick={function(){cosmetic(key)}} style={{padding:14,color:'inherit',border:'1px solid var(--border)'}}><div style={{fontSize:28}}>{it.icon}</div><b style={{fontSize:11}}>{it.title}</b><div style={{fontSize:9,color:'var(--muted)'}}>{it.cost} سکه • {it.slot}</div></button>})}</div></>}

    {tab==='games'&&<div style={{display:'grid',gap:11}}><div className="glass" style={{padding:0,overflow:'hidden'}}><img src="/assets/sector/brand-hero.webp" alt="Sector Arcade" loading="lazy" style={{width:'100%',display:'block',aspectRatio:'1.8',objectFit:'cover'}}/><div style={{padding:'10px 12px',fontSize:10,color:'var(--muted)'}}>بازی، XP و شادی سکتور به هم وصل هستند.</div></div><MemoryGame finish={finish}/><BatteryGame finish={finish}/><button className="btn btn-gold" onClick={function(){ctx.navigate('games')}}>🎮 ورود به آرکید کامل سکتورلند</button><div className="glass" style={{padding:12,fontSize:10,color:'var(--muted)'}}>هر بازی روزانه ۵ بار جایزه می‌دهد. امتیاز به شادی، XP و مأموریت روزانه اضافه می‌شود.</div></div>}

    {tab==='social'&&<><div className="glass" style={{padding:15}}><b>🤝 ارتباط سکتورها</b><p style={{fontSize:10,color:'var(--muted)',lineHeight:1.8}}>نام کاربری دوستت را وارد کن؛ او باید قبلاً ربات را استارت کرده باشد.</p><input value={target} onChange={function(e){setTarget(e.target.value)}} placeholder="@username" style={{width:'100%',boxSizing:'border-box',padding:11,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'white'}}/><div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:6,marginTop:9}}><button className="btn btn-primary" onClick={function(){social('visit')}}>🏠 بازدید</button><button className="btn btn-gold" onClick={function(){social('gift')}}>🎁 هدیه</button><button className="btn" onClick={function(){social('battle')}}>⚔️ نبرد</button></div></div><div className="glass" style={{padding:15,marginTop:10}}><b>🛡 تیم سکتورها</b>{data.clan?<p>عضو تیم <b>{data.clan.name}</b> • XP تیم {data.clan.xp}</p>:<><input value={clanName} onChange={function(e){setClanName(e.target.value)}} placeholder="نام تیم" style={{width:'100%',boxSizing:'border-box',padding:10,marginTop:8,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'white'}}/><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:7,marginTop:7}}><button className="btn btn-primary" onClick={function(){clan('create')}}>ساخت تیم</button><button className="btn" onClick={function(){clan('join')}}>پیوستن</button></div></>}</div><button className="btn btn-gold" onClick={showLeaders} style={{width:'100%',marginTop:10}}>🏆 رتبه‌بندی سکتورها</button>{leaderboard.length>0&&<div className="glass" style={{padding:12,marginTop:8}}>{leaderboard.slice(0,10).map(function(x){return <div key={x.rank} style={{display:'flex',justifyContent:'space-between',fontSize:10,padding:6}}><span>{x.rank}. {x.name} — {x.owner}</span><b>سطح {x.level}</b></div>})}</div>}</>}

    {tab==='memories'&&<div className="glass" style={{padding:14}}><b>📔 دفتر خاطرات {pet.name}</b>{(data.memories||[]).length===0?<p style={{fontSize:11,color:'var(--muted)'}}>هنوز خاطره مهمی ثبت نشده؛ داستان را شروع کن یا مسیر تکامل را انتخاب کن.</p>:(data.memories||[]).map(function(m){return <div key={m.id} style={{padding:'10px 0',borderBottom:'1px solid var(--border)'}}><b style={{fontSize:11}}>{m.kind==='story'?'📖':m.kind==='evolution'?'🧬':'✨'} {m.title}</b><div style={{fontSize:9,color:'var(--muted)',marginTop:4}}>{m.detail}</div></div>})}</div>}

    {tab==='talk'&&<><div className="glass" style={{padding:14}}><b>💬 گفت‌وگوی خصوصی با {pet.name}</b><p style={{fontSize:10,color:'var(--muted)'}}>حافظه و شخصیت این همراه مستقل از هوش عمومی ربات است.</p>{chat.map(function(m,i){return <div key={i} style={{marginTop:8,padding:'9px 11px',borderRadius:12,background:m.role==='user'?'rgba(79,123,255,.18)':'rgba(34,216,122,.12)',fontSize:12,marginRight:m.role==='user'?24:0,marginLeft:m.role==='pet'?24:0}}>{m.role==='pet'?pet.name+': ':''}{m.text}</div>})}<div style={{display:'flex',gap:7,marginTop:10}}><input value={message} maxLength={700} onKeyDown={function(e){if(e.key==='Enter')talk()}} onChange={function(e){setMessage(e.target.value)}} placeholder={'به '+pet.name+' بگو…'} style={{flex:1,minWidth:0,padding:10,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'white'}}/><button className="btn btn-primary" disabled={busy==='talk'} onClick={talk}>{busy==='talk'?'⏳':'ارسال'}</button></div></div><div className="glass" style={{padding:12,marginTop:10,fontSize:10,color:'var(--muted)'}}>🤝 بازی دونفره و عملیات بانکی از بخش تعامل سکتور در چت ربات هم در دسترس است.</div></>}

    {tab==='command'&&ctx.dbUser.is_admin&&<div className="glass" style={{padding:15}}><b>👑 مرکز فرماندهی سکتورها</b><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,margin:'12px 0'}}><div className="glass" style={{padding:12,textAlign:'center'}}><b>{admin&&admin.pets||0}</b><small style={{display:'block'}}>کل سکتورها</small></div><div className="glass" style={{padding:12,textAlign:'center'}}><b>{admin&&admin.active_today||0}</b><small style={{display:'block'}}>فعال امروز</small></div></div><label style={{fontSize:10}}>عنوان رویداد زنده</label><input value={eventTitle} onChange={function(e){setEventTitle(e.target.value)}} style={{width:'100%',boxSizing:'border-box',padding:11,marginTop:6,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'white'}}/><button className="btn btn-gold" onClick={saveEvent} style={{width:'100%',marginTop:9}}>ذخیره رویداد</button><div style={{borderTop:'1px solid var(--border)',marginTop:14,paddingTop:12}}><label style={{fontSize:10}}>هدیه همگانی به همه صاحبان سکتور</label><input type="number" value={giftAmount} onChange={function(e){setGiftAmount(e.target.value)}} style={{width:'100%',boxSizing:'border-box',padding:10,marginTop:6,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'white'}}/><button className="btn btn-primary" onClick={sendGift} style={{width:'100%',marginTop:7}}>🎁 ارسال هدیه همگانی</button></div></div>}

    <button className="btn" onClick={toggleNotifications} style={{width:'100%',marginTop:10}}>{pet.notifications_enabled?'🔔 اعلان‌های سکتور فعال است':'🔕 اعلان‌های سکتور خاموش است'}</button>
    <div className="glass" style={{padding:12,marginTop:14,fontSize:10,color:'var(--muted)',lineHeight:1.9}}>🧬 {stage.next_gate?'تکامل بعدی: سطح '+stage.next_gate.level+' و '+stage.next_gate.care_days+' روز مراقبت واقعی.':'سکتور به فرم نهایی رسیده است.'} رشد برای ماه‌ها طراحی شده و بازگشت روزانه از تکرار زیاد در یک روز ارزشمندتر است.</div><div style={{height:24}}/>
  </div>
}
