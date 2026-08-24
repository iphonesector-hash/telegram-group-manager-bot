import { useMemo, useState } from 'react'
import { StickerArt } from './SectorVisuals'
import SectorFeatureArt from './SectorFeatureArt'

function TinyBar({value,max=100}){
  const pct=Math.max(0,Math.min(100,Number(value||0)/Math.max(1,Number(max||1))*100))
  return <div className="progress-bar"><div className="progress-fill" style={{width:pct+'%'}}/></div>
}

export default function SectorLongGame({meta,busy,onAttack,onClaim,onStory,onRefresh,onClaimPreviousSeason,seasonBoard,onSeasonBoard}){
  const [refreshing,setRefreshing]=useState(false),[refreshed,setRefreshed]=useState(false)
  const season=meta?.season||{}
  const boss=meta?.boss||{}
  const missions=meta?.missions||[]
  const quests=meta?.quests||[]
  const bonds=meta?.bonds||[]
  const notices=meta?.notices||[]
  const previous=meta?.previous_season||{}
  const hpPct=useMemo(()=>Math.max(0,Math.min(100,Number(boss.hp||0)/Math.max(1,Number(boss.max_hp||1))*100)),[boss.hp,boss.max_hp])
  async function refresh(){setRefreshing(true);setRefreshed(false);try{await onRefresh();setRefreshed(true);setTimeout(()=>setRefreshed(false),1800)}finally{setRefreshing(false)}}
  return <>
    {notices.length>0&&<div className="glass" style={{padding:12,marginBottom:10}}>{notices.map((n,i)=><div key={i} style={{fontSize:10,lineHeight:1.8,padding:'5px 0'}}>• {n.text}</div>)}</div>}

    {previous.eligible&&<div className="glass" style={{padding:12,marginBottom:10}}><div style={{display:'flex',alignItems:'center',gap:10}}><StickerArt kind="reward" compact/><div style={{flex:1}}><div style={{fontSize:9,color:'var(--muted)'}}>فصل قبل {previous.season_key}</div><b>رتبه {previous.rank} • {previous.points} SP</b></div><button className="btn" disabled={previous.claimed||!!busy} onClick={onClaimPreviousSeason}>{previous.claimed?'دریافت شده':'دریافت جایزه'}</button></div></div>}
    <div className="glass sector-season-intro" style={{padding:14}}>
      <div className="sector-season-help"><b>فصل چیست؟</b><span>یک رقابت ماهانه است. مأموریت‌ها را کامل کن، جایزه‌شان را بگیر و SP جمع کن؛ SP رتبه تو را در جدول فصل بالا می‌برد.</span></div>
      <div style={{display:'flex',alignItems:'center',gap:10}}><StickerArt kind="victory" compact/><div style={{flex:1}}><div style={{fontSize:9,color:'var(--muted)'}}>SEASON</div><b>{season.title||'Sector Season'}</b></div><div style={{textAlign:'left'}}><b>{Number(season.points||0).toLocaleString('fa-IR')} SP</b><div style={{fontSize:9,color:'var(--muted)'}}>رتبه {season.rank||'-'} از {season.participants||0}</div></div></div>
      <div style={{display:'flex',justifyContent:'space-between',fontSize:9,color:'var(--muted)',marginTop:10}}><span>{season.key||''}</span><span>{season.days_left??'-'} روز باقی‌مانده</span></div>
      <button className="btn" style={{width:'100%',marginTop:10}} onClick={onSeasonBoard}>جدول فصل</button>
      {seasonBoard?.length>0&&<div style={{marginTop:8}}>{seasonBoard.slice(0,10).map(x=><div key={x.rank} style={{display:'flex',justifyContent:'space-between',fontSize:10,padding:'7px 0',borderBottom:'1px solid var(--border)'}}><span>{x.rank}. {x.name} — {x.owner}</span><b>{x.points} SP</b></div>)}</div>}
    </div>

    <div className="glass" style={{padding:14,marginTop:10,background:'linear-gradient(160deg,rgba(45,17,28,.82),rgba(12,12,18,.96))'}}>
      <SectorFeatureArt kind="boss"/>
      <div style={{display:'flex',alignItems:'center',gap:10}}><StickerArt kind="boss" compact/><div style={{flex:1}}><div style={{fontSize:9,color:'#c98596'}}>WORLD BOSS</div><b>{boss.title||'VOID WARDEN'}</b></div><span style={{fontSize:9,color:'var(--muted)'}}>Damage تو: {Number(boss.my_damage||0).toLocaleString('fa-IR')}</span></div>
      <div style={{marginTop:10}}><TinyBar value={boss.hp} max={boss.max_hp}/></div>
      <div style={{display:'flex',justifyContent:'space-between',fontSize:9,marginTop:6}}><span>{Number(boss.hp||0).toLocaleString('fa-IR')} HP</span><span>{hpPct.toFixed(0)}%</span></div>
      <button className="btn btn-primary" style={{width:'100%',marginTop:10}} disabled={!!busy||!boss.active||Number(boss.cooldown_seconds||0)>0} onClick={onAttack}>{!boss.active?'Boss شکست خورده':Number(boss.cooldown_seconds||0)>0?'خنک‌سازی '+Math.ceil(Number(boss.cooldown_seconds)/60)+' دقیقه':'حمله — ۱۰ انرژی'}</button>
      {boss.leaders?.length>0&&<div style={{marginTop:10}}>{boss.leaders.map((x,i)=><div key={x.user_id} style={{display:'flex',justifyContent:'space-between',fontSize:9,padding:'5px 0'}}><span>{i+1}. {x.name}</span><b>{Number(x.damage).toLocaleString('fa-IR')}</b></div>)}</div>}
    </div>

    <div className="sec-title">قدم‌های کسب امتیاز فصل</div>
    <div className="glass" style={{padding:12}}><SectorFeatureArt kind="mission"/><div style={{display:'flex',alignItems:'center',gap:8,margin:'8px 0 6px'}}><StickerArt kind="mission" compact/><div style={{fontSize:9,color:'var(--muted)'}}>ماموریت‌ها با مراقبت، بازی و تعامل اجتماعی جلو می‌روند.</div></div>{missions.map(m=><div key={m.id} style={{padding:'10px 0',borderBottom:'1px solid var(--border)'}}><div style={{display:'flex',justifyContent:'space-between',gap:10}}><b style={{fontSize:10}}>{m.title}</b><span style={{fontSize:9}}>{m.progress}/{m.target}</span></div><TinyBar value={m.progress} max={m.target}/><div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:7}}><span style={{fontSize:8,color:'var(--muted)'}}>+{m.reward?.coins} سکه • +{m.reward?.xp} XP • +{m.reward?.season} SP</span><button className="btn" disabled={!m.complete||m.claimed||!!busy} onClick={()=>onClaim('mission',m.id)}>{m.claimed?'گرفته شد':'دریافت'}</button></div></div>)}</div>

    <div className="sec-title">دستاوردهای بلندمدت</div>
    <div className="glass" style={{padding:12}}><SectorFeatureArt kind="story"/><p style={{fontSize:9,color:'var(--muted)',lineHeight:1.8}}>این هدف‌ها تاریخ انقضا ندارند. با رشد، خرید قطعه، دوستی و داستان کامل می‌شوند.</p>{quests.map(q=><div key={q.id} style={{padding:'9px 0',borderBottom:'1px solid var(--border)'}}><div style={{display:'flex',justifyContent:'space-between',gap:8}}><div><b style={{fontSize:10}}>{q.title}</b><div style={{fontSize:8,color:'var(--muted)',marginTop:3}}>{q.hint}</div></div><button className="btn" disabled={!q.complete||q.claimed||!!busy} onClick={()=>onClaim('quest',q.id)}>{q.claimed?'گرفته شد':'جایزه'}</button></div></div>)}</div>

    <div className="sec-title">Bond</div>
    <div className="glass" style={{padding:12}}>{bonds.length===0?<><SectorFeatureArt kind="bond"/><div style={{display:'flex',alignItems:'center',gap:8,marginTop:8}}><StickerArt kind="love" compact/><div style={{fontSize:10,color:'var(--muted)',padding:8}}>هنوز Bond فعالی نداری. ملاقات، هدیه و دوئل با کاربران دیگر پیوند می‌سازد.</div></div></>:bonds.map(b=><div key={b.user_id} style={{padding:'8px 0',borderBottom:'1px solid var(--border)'}}><div style={{display:'flex',justifyContent:'space-between'}}><b style={{fontSize:10}}>{b.name}</b><span style={{fontSize:9}}>Bond Lv.{b.level}</span></div><TinyBar value={b.xp%100} max={100}/><div style={{fontSize:8,color:'var(--muted)',marginTop:4}}>{b.interactions} تعامل • {b.gifts} هدیه • {b.battles} دوئل • {b.visits} ملاقات</div></div>)}</div>

    <button className="btn sector-season-refresh" disabled={refreshing} onClick={refresh}>{refreshing?'در حال دریافت اطلاعات…':refreshed?'✓ اطلاعات فصل به‌روز شد':'به‌روزرسانی اطلاعات فصل'}</button>
  </>
}
