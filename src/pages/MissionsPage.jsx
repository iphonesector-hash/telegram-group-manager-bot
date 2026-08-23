import { useEffect, useState } from 'react'
import { useAppContext } from '../App'

export default function MissionsPage(){
  var ctx=useAppContext(),user=ctx.tgUser
  var [items,setItems]=useState([]),[loading,setLoading]=useState(true),[claiming,setClaiming]=useState('')
  function load(){if(!user)return;setLoading(true);ctx.apiCall('getMissions',user.id).then(function(r){setItems(Array.isArray(r&&r.data)?r.data:[]);setLoading(false)})}
  useEffect(load,[user,ctx.apiCall])
  function claim(m){if(claiming||!m.complete||m.claimed)return;setClaiming(m.id);ctx.apiCall('claimMission',user.id,m.id).then(function(r){var d=r&&r.data;if(d&&d.status==='success'){ctx.showToast(`🎁 +${d.reward.coins} سکه و +${d.reward.xp} XP`,'success');ctx.refreshUser();load()}else ctx.showToast((d&&d.message)||(r&&r.error)||'دریافت جایزه انجام نشد.','error');setClaiming('')})}
  if(loading)return <div className="page"><div className="glass" style={{padding:24,textAlign:'center'}}>⏳ در حال دریافت مأموریت‌ها...</div></div>
  return <div className="page fade-up">
    <div className="glass" style={{padding:18,marginBottom:14,background:'linear-gradient(135deg,rgba(34,216,122,.13),rgba(79,123,255,.13))'}}><div style={{fontWeight:900,fontSize:19}}>ماموریت‌های SectorLand</div><div style={{fontSize:11,color:'var(--muted)',lineHeight:1.8,marginTop:5}}>با فعالیت واقعی در ربات و مینی‌اپ، سکه و XP دریافت کن.</div></div>
    {['daily','weekly'].map(function(period){var list=items.filter(function(x){return x.period===period});return <div key={period}><div className="sec-title">{period==='daily'?'☀️ روزانه':'📅 هفتگی'}</div>{list.map(function(m){var pct=Math.min(100,Math.round(m.progress/Math.max(1,m.target)*100));return <div className="glass" key={m.id} style={{padding:14,marginBottom:9,border:m.complete?'1px solid rgba(34,216,122,.35)':'1px solid var(--border)'}}><div style={{display:'flex',alignItems:'center',gap:10}}><div style={{fontSize:24}}>{m.kind==='quiz'?'🧠':m.kind==='tools'?'🤖':'🎡'}</div><div style={{flex:1}}><div style={{fontWeight:800,fontSize:13}}>{m.title}</div><div style={{fontSize:10,color:'var(--muted)',marginTop:3}}>جایزه: {m.coins} 🪙 + {m.xp} XP</div></div><div style={{fontSize:11,fontWeight:800}}>{m.progress}/{m.target}</div></div><div className="progress-bar" style={{marginTop:10}}><div className="progress-fill" style={{width:pct+'%'}}/></div><button className="btn" disabled={!m.complete||m.claimed||claiming===m.id} onClick={function(){claim(m)}} style={{width:'100%',marginTop:10,background:m.claimed?'rgba(255,255,255,.05)':m.complete?'linear-gradient(135deg,var(--green),#0aa86b)':'var(--card)',color:m.complete?'#fff':'var(--muted)',border:'1px solid var(--border)'}}>{m.claimed?'✅ دریافت‌شده':claiming===m.id?'⏳ در حال ثبت...':m.complete?'🎁 دریافت جایزه':'در حال انجام'}</button></div>})}</div>})}
    <div style={{height:20}}/>
  </div>
}
