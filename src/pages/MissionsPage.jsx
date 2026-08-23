import { useEffect, useState } from 'react'
import { useAppContext } from '../App'
import SectorCelebration from '../components/ui/SectorCelebration'

export default function MissionsPage(){
  var ctx=useAppContext(),user=ctx.tgUser
  var [items,setItems]=useState([]),[loading,setLoading]=useState(true),[claiming,setClaiming]=useState('')
  var [celebration,setCelebration]=useState(null)
  function load(){if(!user)return;setLoading(true);ctx.apiCall('getMissions',user.id).then(function(r){setItems(Array.isArray(r&&r.data)?r.data:[]);setLoading(false)})}
  useEffect(load,[user,ctx.apiCall])
  function claim(m){if(claiming||!m.complete||m.claimed)return;setClaiming(m.id);ctx.apiCall('claimMission',user.id,m.id).then(function(r){var d=r&&r.data;if(d&&d.status==='success'){var coins=Number(d.reward.coins||0),xp=Number(d.reward.xp||0);ctx.showToast(`🎁 +${coins} سکه و +${xp} XP`,'success');setCelebration({title:'ماموریت کامل شد! ✨',text:`+${coins.toLocaleString('fa-IR')} سکه و +${xp.toLocaleString('fa-IR')} XP به حسابت اضافه شد.`});ctx.refreshUser();load()}else ctx.showToast((d&&d.message)||(r&&r.error)||'دریافت جایزه انجام نشد.','error');setClaiming('')})}
  if(loading)return <div className="page"><div className="glass" style={{padding:24,textAlign:'center'}}>⏳ در حال دریافت مأموریت‌ها...</div></div>
  var completed=items.filter(function(x){return x.complete}).length
  return <div className="page fade-up">
    <SectorCelebration open={!!celebration} title={celebration&&celebration.title} text={celebration&&celebration.text} onClose={function(){setCelebration(null)}} />

    <div className="glass" style={{padding:0,marginBottom:14,overflow:'hidden',border:'1px solid rgba(125,92,255,.35)',background:'#090c27'}}>
      <div style={{position:'relative',height:150,overflow:'hidden'}}>
        <img src="/assets/sector/brand-hero.webp" alt="Sector missions" style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:'center 42%',filter:'saturate(1.08)'}} />
        <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,rgba(5,7,27,.08),rgba(5,7,27,.92))'}} />
        <div style={{position:'absolute',right:16,left:16,bottom:13}}>
          <div style={{fontWeight:950,fontSize:19}}>🎯 ماموریت‌های SectorLand</div>
          <div style={{fontSize:10,color:'rgba(255,255,255,.72)',marginTop:4}}>بازی کن • رشد کن • جایزه بگیر</div>
        </div>
      </div>
      <div style={{padding:'12px 14px',display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8,textAlign:'center'}}>
        <div><b>{items.length.toLocaleString('fa-IR')}</b><small style={{display:'block',color:'var(--muted)',marginTop:2}}>کل ماموریت</small></div>
        <div><b style={{color:'var(--green)'}}>{completed.toLocaleString('fa-IR')}</b><small style={{display:'block',color:'var(--muted)',marginTop:2}}>تکمیل‌شده</small></div>
        <div><b style={{color:'var(--gold)'}}>{Math.max(0,items.length-completed).toLocaleString('fa-IR')}</b><small style={{display:'block',color:'var(--muted)',marginTop:2}}>باقی‌مانده</small></div>
      </div>
    </div>

    {['daily','weekly'].map(function(period){var list=items.filter(function(x){return x.period===period});return <div key={period}><div className="sec-title">{period==='daily'?'☀️ روزانه':'📅 هفتگی'}</div>{list.map(function(m){var pct=Math.min(100,Math.round(m.progress/Math.max(1,m.target)*100));return <div className="glass" key={m.id} style={{padding:14,marginBottom:9,border:m.complete?'1px solid rgba(34,216,122,.35)':'1px solid var(--border)',background:m.complete?'linear-gradient(135deg,rgba(34,216,122,.06),rgba(79,123,255,.06))':undefined}}><div style={{display:'flex',alignItems:'center',gap:10}}><div style={{fontSize:24}}>{m.kind==='quiz'?'🧠':m.kind==='tools'?'🤖':'🎡'}</div><div style={{flex:1}}><div style={{fontWeight:800,fontSize:13}}>{m.title}</div><div style={{fontSize:10,color:'var(--muted)',marginTop:3}}>جایزه: {m.coins} 🪙 + {m.xp} XP</div></div><div style={{fontSize:11,fontWeight:800}}>{m.progress}/{m.target}</div></div><div className="progress-bar" style={{marginTop:10}}><div className="progress-fill" style={{width:pct+'%'}}/></div><button className="btn" disabled={!m.complete||m.claimed||claiming===m.id} onClick={function(){claim(m)}} style={{width:'100%',marginTop:10,background:m.claimed?'rgba(255,255,255,.05)':m.complete?'linear-gradient(135deg,var(--green),#0aa86b)':'var(--card)',color:m.complete?'#fff':'var(--muted)',border:'1px solid var(--border)'}}>{m.claimed?'✅ دریافت‌شده':claiming===m.id?'⏳ در حال ثبت...':m.complete?'🎁 دریافت جایزه':'در حال انجام'}</button></div>})}</div>})}

    <div className="glass" style={{padding:'12px 12px 9px',marginTop:8,overflow:'hidden'}}>
      <div style={{fontWeight:900,fontSize:12,marginBottom:8}}>🏆 رتبه‌های قابل دستیابی</div>
      <img src="/assets/sector/rank-badges.webp" alt="Sector ranks" loading="lazy" style={{display:'block',width:'100%',borderRadius:10}} />
    </div>
    <div style={{height:20}}/>
  </div>
}
