import {useState} from 'react'
import SectorIcon from '../ui/SectorIcon'

const ROUTE_ICON={identity:'sectorpet',care:'care',games:'games',command:'command',shop:'shop',season:'season',social:'social',growth:'growth',talk:'talk',home:'home'}
const ROUTE_LABEL={identity:'هویت',care:'مراقبت',games:'چالش‌ها',command:'مرکز فرمان',shop:'قطعات',season:'فصل و باس',social:'اجتماع',growth:'رشد',talk:'گفتگو',home:'داستان'}

function smartObjective(scene,pet){
  if(!scene)return ''
  if(scene.ready)return 'همه شرط‌های این مرحله انجام شده؛ بخش بعدی داستان را باز کن.'
  const health=Number(pet?.health||0),energy=Number(pet?.energy||0)
  if(scene.action==='train_ready'){
    if(health>=60)return `سلامت آماده است (${Math.round(health)}٪). فقط در بخش «مراقبت» یک تمرین انجام بده.`
    return `دو کار باقی مانده: یک تمرین در بخش «مراقبت» انجام بده و سلامت سکتور را از ${Math.round(health)}٪ به حداقل ۶۰٪ برسان.`
  }
  if(scene.action==='core_ready'){
    if(health>=70&&energy<70)return `سلامت آماده است (${Math.round(health)}٪). فقط انرژی را از ${Math.round(energy)}٪ به حداقل ۷۰٪ برسان.`
    if(energy>=70&&health<70)return `انرژی آماده است (${Math.round(energy)}٪). فقط سلامت را از ${Math.round(health)}٪ به حداقل ۷۰٪ برسان.`
  }
  if(scene.action==='boss_ready'&&energy>=20)return 'انرژی کافی است؛ فقط یک حمله به باس جهانی ثبت کن.'
  return scene.objective||''
}

export default function SectorNarrativeHub({narrative,pet,actions=[],busy,onNavigate,onAdvance,onRename}){
  const [name,setName]=useState(''),[help,setHelp]=useState(false),scene=narrative?.scene,chapter=narrative?.chapter_info,world=narrative?.world_info
  if(!scene||!chapter||!world)return null
  const needsName=scene.action==='rename'&&!scene.ready,care=actions.find(x=>x.id===scene.target),cost=Number(care?.cost||0),route=scene.route||'home',routeLabel=ROUTE_LABEL[route]||'بخش مربوط',objectiveText=smartObjective(scene,pet)
  function primary(){if(scene.ready){onAdvance();return}onNavigate(route)}
  return <section className={'sector-narrative glass'+(scene.threat?' is-threat':'')} style={{'--world-color':world.color||'#54dfff'}}>
    <div className="sector-narrative__scan" aria-hidden="true"/>
    <header><div className="sector-narrative__world"><i/><SectorIcon name={scene.threat?'shield':'command'} size={27}/></div><div><small>WORLD {Number(narrative.world).toLocaleString('fa-IR')} · CHAPTER {Number(narrative.chapter).toLocaleString('fa-IR')}</small><h2>{world.title}</h2><span>{chapter.title} · {chapter.region}</span></div><b>{Number(narrative.progress_percent||0).toLocaleString('fa-IR')}٪</b></header>
    <div className="sector-narrative__chapters" aria-label="مسیر هشت فصل">{Array.from({length:8},function(_,i){const n=i+1;return <i key={n} className={n<narrative.chapter?'done':n===narrative.chapter?'current':''}><span>{n<narrative.chapter?'✓':n}</span></i>})}</div>
    <div className="sector-narrative__scene-map" aria-label="مسیر فصل">{Array.from({length:scene.total||5},(_,i)=><span key={i} className={i<scene.index?'done':i===scene.index?'current':''}><i>{i<scene.index?'✓':i+1}</i><small>{i===scene.index?'الان':i<scene.index?'تمام':'بعدی'}</small></span>)}</div>
    {scene.threat?<div className="sector-narrative__alert"><SectorIcon name="shield" size={17}/><b>{scene.threat}</b><span>سامانه دفاعی آماده‌باش</span></div>:null}
    <article><small>صحنه {scene.number||1} از {scene.total||1}</small><h3>{scene.title}</h3><p>{scene.text}</p><blockquote><SectorIcon name="sectorpet" size={18}/><span><b>{pet.name}</b>«{objectiveText}»</span></blockquote></article>
    <div className="sector-narrative__reward"><span><SectorIcon name="coin" size={15}/>{Number(scene.reward?.coins||0).toLocaleString('fa-IR')} سکه</span><span><SectorIcon name="growth" size={15}/>{Number(scene.reward?.xp||0).toLocaleString('fa-IR')} XP</span><span className={scene.ready?'ready':''}>{scene.ready?'هدف انجام شده':'هدف در انتظار'}</span></div>
    {cost?<div className="sector-narrative__cost"><SectorIcon name="coin" size={15}/><span>هزینه این حرکت</span><b>{cost.toLocaleString('fa-IR')} سکه</b></div>:null}
    {help?<div className="sector-narrative__help"><b>الان دقیقاً چه کار کنم؟</b><p>{objectiveText}</p><span>{scene.ready?'همه شرط‌ها انجام شده‌اند؛ دکمه اصلی بخش بعدی را باز می‌کند.':`دکمه اصلی تو را به «${routeLabel}» می‌برد. بعد از انجام کار، وضعیت داستان دوباره بررسی می‌شود.`}</span></div>:null}
    {needsName?<form className="sector-narrative__rename" onSubmit={function(e){e.preventDefault();if(name.trim())onRename(name.trim(),function(){setName('')})}}><label htmlFor="sector-first-name">اسم رفیق جدیدت</label><div><input id="sector-first-name" value={name} onChange={function(e){setName(e.target.value)}} minLength={2} maxLength={20} placeholder="مثلاً آریو"/><button disabled={!!busy||name.trim().length<2}>ثبت نام</button></div></form>:<button className={'sector-narrative__primary'+(scene.ready?' ready':'')} disabled={!!busy} onClick={primary}><SectorIcon name={scene.ready?'story':(ROUTE_ICON[route]||'mission')} size={19}/><span>{scene.ready?'بازکردن بخش بعدی':`برو به ${routeLabel}`}</span><b>‹</b></button>}
    <footer><button onClick={()=>setHelp(v=>!v)}><SectorIcon name="mission" size={15}/> الان چه کار کنم؟</button><button onClick={function(){onNavigate('talk')}}><SectorIcon name="talk" size={15}/> گفت‌وگو با {pet.name}</button></footer>
  </section>
}
