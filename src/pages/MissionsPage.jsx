import { useEffect, useState } from 'react'
import { useAppContext } from '../App'
import SectorCelebration from '../components/ui/SectorCelebration'
import SectorIcon from '../components/ui/SectorIcon'
import SectorRankTrack from '../components/ui/SectorRankTrack'

const KIND_META={quiz:['knowledge','مسابقه'],tools:['tools','ابزار'],game:['games','بازی'],wheel:['refresh','گردونه'],care:['care','مراقبت'],message:['talk','گفت‌وگو'],daily:['mission','روزانه'],weekly:['trophy','هفتگی']}

function MissionTimer({seconds}){
  const [left,setLeft]=useState(Math.max(0,Number(seconds||0)))
  useEffect(function(){setLeft(Math.max(0,Number(seconds||0)));if(!seconds)return;const id=window.setInterval(function(){setLeft(function(v){return Math.max(0,v-1)})},1000);return function(){window.clearInterval(id)}},[seconds])
  if(!seconds)return <span>بدون محدودیت زمانی</span>
  const h=Math.floor(left/3600),m=Math.floor(left%3600/60),s=left%60
  return <time>{[h,m,s].map(function(x){return String(x).padStart(2,'0')}).join(':')}</time>
}

export default function MissionsPage(){
  const ctx=useAppContext(),user=ctx.tgUser
  const [items,setItems]=useState([]),[loading,setLoading]=useState(true),[claiming,setClaiming]=useState(''),[celebration,setCelebration]=useState(null)
  function load(){if(!user)return;setLoading(true);ctx.apiCall('getMissions',user.id).then(function(r){setItems(Array.isArray(r&&r.data)?r.data:[])}).finally(function(){setLoading(false)})}
  useEffect(load,[user,ctx.apiCall])
  function claim(m){if(claiming||!m.complete||m.claimed)return;setClaiming(m.id);ctx.apiCall('claimMission',user.id,m.id).then(function(r){const d=r&&r.data;if(d&&d.status==='success'){const coins=Number(d.reward.coins||0),xp=Number(d.reward.xp||0);ctx.showToast(`+${coins} سکه و +${xp} XP`,'success');setCelebration({title:'ماموریت کامل شد! ✨',text:`+${coins.toLocaleString('fa-IR')} سکه و +${xp.toLocaleString('fa-IR')} XP ثبت شد.`});ctx.refreshUser();load()}else ctx.showToast((d&&d.message)||(r&&r.error)||'دریافت جایزه انجام نشد.','error')}).finally(function(){setClaiming('')})}
  function go(m){const kind=String(m.kind||m.metric||'');ctx.navigate(kind.includes('game')||kind.includes('quiz')?'games':kind.includes('care')||kind.includes('sector')?'sectorpet':kind.includes('tool')?'tools':'home')}
  if(loading)return <div className="page"><div className="mission-loading glass"><SectorIcon name="missions" size={34}/><b>مرکز مأموریت در حال همگام‌سازی است</b></div></div>
  const completed=items.filter(function(x){return x.complete}).length,claimed=items.filter(function(x){return x.claimed}).length,next=items.find(function(x){return x.complete&&!x.claimed})||items.find(function(x){return !x.complete}),progress=items.length?Math.round(completed/items.length*100):0
  return <div className="page fade-up">
    <SectorCelebration open={!!celebration} title={celebration&&celebration.title} text={celebration&&celebration.text} onClose={function(){setCelebration(null)}} />
    <section className="glass mission-hub"><div className="mission-hub__radar"><SectorIcon name="missions" size={36}/><i/><i/></div><div><small>MISSION CONTROL</small><h2>ماموریت‌های من</h2><p>{next?next.complete?'جایزه آماده دریافت داری.':`حرکت بعدی: ${next.title}`:'تمام مأموریت‌های فعال تکمیل شده‌اند.'}</p></div><strong>{progress.toLocaleString('fa-IR')}٪</strong></section>
    {next?<section className={'glass mission-next'+(next.complete?' ready':'')}><header><span><SectorIcon name={next.complete?'gift':(KIND_META[next.kind]||KIND_META.daily)[0]} size={24}/></span><div><small>{next.complete?'REWARD READY':'NEXT ACTION'}</small><h3>{next.title}</h3></div></header><p>{next.description||next.desc||'این حرکت را انجام بده تا مسیر امروز ادامه پیدا کند.'}</p><footer><b>{Number(next.coins||0).toLocaleString('fa-IR')} سکه + {Number(next.xp||0).toLocaleString('fa-IR')} XP</b>{next.complete&&!next.claimed?<button onClick={function(){claim(next)}} disabled={!!claiming}>دریافت جایزه</button>:<button onClick={function(){go(next)}}>انجام حرکت</button>}</footer></section>:null}
    <section className="mission-summary">{[[items.length,'کل','missions'],[completed,'تکمیل','equip'],[claimed,'دریافت','gift']].map(function(x){return <div className="glass" key={x[1]}><SectorIcon name={x[2]} size={19}/><b>{x[0].toLocaleString('fa-IR')}</b><small>{x[1]}</small></div>})}</section>
    {['daily','weekly'].map(function(period){const list=items.filter(function(x){return x.period===period});if(!list.length)return null;return <section className="mission-group" key={period}><header><div><SectorIcon name={period==='daily'?'mission':'trophy'} size={19}/><b>{period==='daily'?'ماموریت‌های روزانه':'ماموریت‌های هفتگی'}</b></div><MissionTimer seconds={list[0]&&list[0].reset_seconds}/></header>{list.map(function(m){const pct=Math.min(100,Math.round(Number(m.progress||0)/Math.max(1,Number(m.target||1))*100)),meta=KIND_META[m.kind]||KIND_META[period];return <article className={'glass mission-card'+(m.complete?' complete':'')+(m.claimed?' claimed':'')} key={m.id}><span className="mission-card__icon"><SectorIcon name={meta[0]} size={22}/></span><div className="mission-card__body"><small>{meta[1]}</small><b>{m.title}</b><div className="mission-card__bar"><i style={{width:pct+'%'}}/></div><footer><span>{Number(m.progress||0).toLocaleString('fa-IR')}/{Number(m.target||1).toLocaleString('fa-IR')}</span><strong>{Number(m.coins||0).toLocaleString('fa-IR')} سکه · {Number(m.xp||0).toLocaleString('fa-IR')} XP</strong></footer></div><button disabled={m.claimed||claiming===m.id} onClick={function(){m.complete?claim(m):go(m)}}>{m.claimed?'✓':claiming===m.id?'…':m.complete?'دریافت':'ادامه'}</button></article>})}</section>})}
    <SectorRankTrack level={Number(ctx.dbUser.level||1)}/><div style={{height:18}}/>
  </div>
}
