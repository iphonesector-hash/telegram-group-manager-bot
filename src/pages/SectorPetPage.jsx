import { useEffect, useState } from 'react'
import { useAppContext } from '../App'

const ICONS={charge:'⚡',play:'🎮',train:'🏋️',learn:'🧠',repair:'🔧'}
const STAT_ICONS={energy:'⚡',happiness:'💙',knowledge:'🧠',health:'❤️'}
const STAT_NAMES={energy:'انرژی',happiness:'شادی',knowledge:'دانش',health:'سلامتی'}

export default function SectorPetPage(){
  var ctx=useAppContext(),user=ctx.tgUser
  var [data,setData]=useState(null),[busy,setBusy]=useState(''),[newName,setNewName]=useState(''),[message,setMessage]=useState(''),[chat,setChat]=useState([])
  function load(){if(!user)return;ctx.apiCall('getSectorPet',user.id).then(function(r){if(r&&r.data)setData(r.data)})}
  useEffect(load,[user,ctx.apiCall])
  function act(id){if(busy)return;setBusy(id);ctx.apiCall('sectorPetAction',user.id,id).then(function(r){var d=r&&r.data;if(d&&d.status==='success'){setData(function(v){return {...v,pet:d.pet,daily:d.daily||v.daily}});ctx.setDbUser(function(u){return {...u,coins:Number(d.coins)}});ctx.showToast(d.message,'success')}else ctx.showToast((d&&d.message)||(r&&r.error)||'سکتور نتوانست این کار را انجام دهد.','error');setBusy('')})}
  function rename(){var name=newName.trim();if(!name)return;setBusy('rename');ctx.apiCall('renameSectorPet',user.id,name).then(function(r){var d=r&&r.data;if(d&&d.status==='success'){setData(function(v){return {...v,pet:d.pet}});setNewName('');ctx.showToast(d.message,'success')}else ctx.showToast((r&&r.error)||'نام تغییر نکرد','error');setBusy('')})}
  function talk(){var text=message.trim();if(!text||busy)return;setMessage('');setChat(function(v){return v.concat({role:'user',text:text})});setBusy('talk');ctx.apiCall('talkSectorPet',user.id,text).then(function(r){var d=r&&r.data;if(d&&d.status==='success')setChat(function(v){return v.concat({role:'pet',text:d.response})});else ctx.showToast((r&&r.error)||'سکتور جواب نداد','error');setBusy('')})}
  if(!data)return <div className="page"><div className="glass" style={{padding:24,textAlign:'center'}}>🤖 در حال بیدار کردن سکتور...</div></div>
  var pet=data.pet,stage=pet.stage||{id:1,title:'سکتور کوچولو'}
  var daily=data.daily||{actions:0,target:3},gate=stage.next_gate
  return <div className="page fade-up">
    <div className="glass" style={{padding:16,overflow:'hidden',textAlign:'center',background:'radial-gradient(circle at 50% 10%,rgba(52,226,255,.18),transparent 50%),linear-gradient(160deg,rgba(35,22,91,.75),rgba(6,12,28,.92))'}}>
      <div style={{fontSize:10,color:'#64efff',fontWeight:900,letterSpacing:1}}>SECTOR COMPANION</div>
      <div style={{fontWeight:900,fontSize:21,marginTop:4}}>{stage.title}</div>
      <div style={{fontSize:11,color:'var(--muted)',marginTop:4}}>سطح {pet.level} • همراه هوشمند شخصی تو</div>
      <img src="/assets/sector-evolution.webp" alt="مراحل رشد ربات سکتور" style={{width:'100%',maxWidth:390,display:'block',margin:'-20px auto -30px',filter:'drop-shadow(0 15px 28px rgba(0,208,255,.24))'}} />
      <div style={{display:'flex',justifyContent:'center',gap:8,marginBottom:12}}>{[1,2,3,4].map(function(n){return <span key={n} style={{width:n===stage.id?28:9,height:9,borderRadius:8,background:n<=stage.id?'#50e8ff':'rgba(255,255,255,.14)',boxShadow:n===stage.id?'0 0 12px #42dbff':'none'}}/>})}</div>
      <div style={{display:'flex',justifyContent:'space-between',fontSize:10,color:'var(--muted)'}}><span>XP سطح</span><span>{pet.xp_in_level} / {pet.xp_next}</span></div>
      <div className="progress-bar" style={{marginTop:6}}><div className="progress-fill" style={{width:Math.min(100,pet.xp_in_level/pet.xp_next*100)+'%'}}/></div>
    </div>
    <div className="glass" style={{padding:14,marginTop:12,display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,textAlign:'center'}}>
      <div><div style={{fontSize:22}}>🔥</div><b>{pet.streak_days||0} روز</b><div style={{fontSize:9,color:'var(--muted)'}}>زنجیره حضور</div></div>
      <div><div style={{fontSize:22}}>📅</div><b>{pet.total_care_days||0} روز</b><div style={{fontSize:9,color:'var(--muted)'}}>مراقبت واقعی</div></div>
    </div>
    <div className="glass" style={{padding:14,marginTop:10,marginBottom:14,borderColor:daily.complete?'rgba(34,216,122,.45)':'var(--border)'}}><div style={{display:'flex',justifyContent:'space-between',fontSize:12,fontWeight:800}}><span>🎯 چالش امروز</span><span>{Math.min(daily.actions,daily.target)} / {daily.target}</span></div><div style={{fontSize:10,color:'var(--muted)',marginTop:7,lineHeight:1.8}}>{daily.complete?'ماموریت مراقبت امروز کامل شد؛ از بخش مأموریت‌ها جایزه‌ات را بگیر.':'امروز سه فعالیت مراقبتی انجام بده.'}</div></div>
    <div className="sec-title" style={{marginTop:16}}>وضعیت سکتور</div>
    <div className="glass" style={{padding:14,marginBottom:14}}>{['energy','happiness','knowledge','health'].map(function(key){var value=Number(pet[key]||0);return <div key={key} style={{marginBottom:11}}><div style={{display:'flex',justifyContent:'space-between',fontSize:11,marginBottom:5}}><span>{STAT_ICONS[key]} {STAT_NAMES[key]}</span><b>{value}%</b></div><div className="progress-bar"><div className="progress-fill" style={{width:value+'%',background:value<25?'linear-gradient(90deg,#ff5578,#ff8d54)':undefined}}/></div></div>})}</div>
    <div className="sec-title">مراقبت و ارتقا</div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9}}>{data.actions.map(function(a){return <button key={a.id} className="glass" disabled={!!busy} onClick={function(){act(a.id)}} style={{padding:14,color:'inherit',border:'1px solid var(--border)',textAlign:'center',cursor:'pointer'}}><div style={{fontSize:28}}>{busy===a.id?'⏳':ICONS[a.id]}</div><div style={{fontWeight:800,fontSize:12,marginTop:5}}>{a.title}</div><div style={{fontSize:9,color:'var(--muted)',marginTop:4}}>{ctx.dbUser.unlimited_wallet?'رایگان برای فرمانده':a.cost+' سکه'} • +{a.xp} XP</div></button>})}</div>
    <div className="glass" style={{padding:14,marginTop:14}}><div style={{fontWeight:800,fontSize:12}}>✏️ اسم مخصوص همراهت</div><div style={{display:'flex',gap:8,marginTop:9}}><input value={newName} maxLength={20} onChange={function(e){setNewName(e.target.value)}} placeholder={pet.name} style={{flex:1,minWidth:0,padding:10,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'var(--text)'}}/><button className="btn btn-primary" disabled={busy==='rename'} onClick={rename}>{busy==='rename'?'⏳':'ثبت'}</button></div></div>
    <div className="glass" style={{padding:14,marginTop:12}}><div style={{fontWeight:900,fontSize:13}}>💬 حرف‌زدن با {pet.name}</div><div style={{fontSize:10,color:'var(--muted)',marginTop:4}}>این خودِ همراه توست و شخصیت و حافظهٔ جدا از دستیار عمومی دارد.</div>{chat.map(function(m,i){return <div key={i} style={{marginTop:9,padding:'9px 11px',borderRadius:12,background:m.role==='user'?'rgba(79,123,255,.18)':'rgba(34,216,122,.12)',fontSize:12,lineHeight:1.8,marginRight:m.role==='user'?24:0,marginLeft:m.role==='pet'?24:0}}>{m.role==='pet'?pet.name+': ':''}{m.text}</div>})}<div style={{display:'flex',gap:8,marginTop:10}}><input value={message} maxLength={700} onKeyDown={function(e){if(e.key==='Enter')talk()}} onChange={function(e){setMessage(e.target.value)}} placeholder={'به '+pet.name+' چیزی بگو…'} style={{flex:1,minWidth:0,padding:10,borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'var(--text)'}}/><button className="btn btn-primary" disabled={busy==='talk'} onClick={talk}>{busy==='talk'?'⏳':'ارسال'}</button></div></div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9,marginTop:10}}><button className="btn btn-primary" onClick={function(){ctx.navigate('missions')}}>🎯 مأموریت‌ها</button><button className="btn btn-gold" onClick={function(){ctx.navigate('games')}}>🎮 بازی‌های کامل</button></div>
    <div className="glass" style={{padding:12,marginTop:10,fontSize:10,color:'var(--muted)',lineHeight:1.9}}>🤝 بازی دونفره و عملیات بانکی نیز از پنل تعاملی سکتور در چت ربات اجرا می‌شوند؛ بازی‌های کامل از دکمه بالا در دسترس‌اند.</div>
    <div className="glass" style={{padding:12,marginTop:14,fontSize:10,color:'var(--muted)',lineHeight:1.9}}>🧬 {gate?'تکامل بعدی به سطح '+gate.level+' و '+gate.care_days+' روز مراقبت نیاز دارد.':'سکتور به فرم نهایی رسیده است.'}<br/>💡 پنج فعالیت اول هر روز XP کامل می‌دهد و ادامه فعالیت XP کمتری دارد؛ بنابراین رشد واقعی با بازگشت روزانه و انجام مأموریت‌ها شکل می‌گیرد.</div>
    <div style={{height:22}}/>
  </div>
}
