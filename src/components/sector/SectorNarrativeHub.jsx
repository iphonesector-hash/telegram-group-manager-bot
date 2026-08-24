import {useState} from 'react'
import SectorIcon from '../ui/SectorIcon'

const ROUTE_ICON={identity:'sectorpet',care:'care',games:'games',command:'command',shop:'shop',season:'season',social:'social',growth:'growth',talk:'talk',home:'home'}

export default function SectorNarrativeHub({narrative,pet,busy,onNavigate,onAdvance,onRename}){
  const [name,setName]=useState(''),scene=narrative?.scene,chapter=narrative?.chapter_info,world=narrative?.world_info
  if(!scene||!chapter||!world)return null
  const needsName=scene.action==='rename'&&!scene.ready
  function primary(){if(scene.ready)return onAdvance();onNavigate(scene.route||'home')}
  return <section className={'sector-narrative glass'+(scene.threat?' is-threat':'')} style={{'--world-color':world.color||'#54dfff'}}>
    <div className="sector-narrative__scan" aria-hidden="true"/>
    <header><div className="sector-narrative__world"><i/><SectorIcon name={scene.threat?'shield':'command'} size={27}/></div><div><small>WORLD {Number(narrative.world).toLocaleString('fa-IR')} · CHAPTER {Number(narrative.chapter).toLocaleString('fa-IR')}</small><h2>{world.title}</h2><span>{chapter.title} · {chapter.region}</span></div><b>{Number(narrative.progress_percent||0).toLocaleString('fa-IR')}٪</b></header>
    <div className="sector-narrative__chapters" aria-label="مسیر هشت فصل">{Array.from({length:8},function(_,i){const n=i+1;return <i key={n} className={n<narrative.chapter?'done':n===narrative.chapter?'current':''}><span>{n<narrative.chapter?'✓':n}</span></i>})}</div>
    {scene.threat?<div className="sector-narrative__alert"><SectorIcon name="shield" size={17}/><b>{scene.threat}</b><span>سامانه دفاعی آماده‌باش</span></div>:null}
    <article><small>صحنه {scene.number||1} از {scene.total||1}</small><h3>{scene.title}</h3><p>{scene.text}</p><blockquote><SectorIcon name="sectorpet" size={18}/><span><b>{pet.name}</b>«{scene.objective}»</span></blockquote></article>
    <div className="sector-narrative__reward"><span><SectorIcon name="coin" size={15}/>{Number(scene.reward?.coins||0).toLocaleString('fa-IR')} سکه</span><span><SectorIcon name="growth" size={15}/>{Number(scene.reward?.xp||0).toLocaleString('fa-IR')} XP</span><span className={scene.ready?'ready':''}>{scene.ready?'هدف انجام شده':'هدف در انتظار'}</span></div>
    {needsName?<form className="sector-narrative__rename" onSubmit={function(e){e.preventDefault();if(name.trim())onRename(name.trim(),function(){setName('')})}}><label htmlFor="sector-first-name">اسم رفیق جدیدت</label><div><input id="sector-first-name" value={name} onChange={function(e){setName(e.target.value)}} minLength={2} maxLength={20} placeholder="مثلاً آریو"/><button disabled={!!busy||name.trim().length<2}>ثبت نام</button></div></form>:<button className={'sector-narrative__primary'+(scene.ready?' ready':'')} disabled={!!busy} onClick={primary}><SectorIcon name={scene.ready?'story':(ROUTE_ICON[scene.route]||'mission')} size={19}/><span>{scene.ready?'بازکردن بخش بعدی':`برو به ${scene.objective.length>34?'بخش مربوط':'هدف'}`}</span><b>‹</b></button>}
    <footer><span>حرکت بعدی همیشه همین‌جا مشخص می‌شود.</span><button onClick={function(){onNavigate('talk')}}><SectorIcon name="talk" size={15}/> گفت‌وگو با {pet.name}</button></footer>
  </section>
}
