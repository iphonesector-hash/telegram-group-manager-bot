import { useState } from 'react'
import { useAppContext } from '../App'

const TABS=[['ai','🤖','دستیار'],['weather','🌤️','هوا'],['translate','🌐','ترجمه'],['calc','🧮','حسابگر'],['convert','⚖️','تبدیل']]
const UNITS={length:{label:'طول',units:{متر:1,کیلومتر:1000,سانتی‌متر:.01,مایل:1609.344,فوت:.3048}},weight:{label:'وزن',units:{کیلوگرم:1,گرم:.001,پوند:.45359237,اونس:.0283495}}}

export default function ToolsPage(){
  var ctx=useAppContext(), user=ctx.tgUser
  var [tab,setTab]=useState('ai'),[busy,setBusy]=useState(false)
  var [input,setInput]=useState(''),[output,setOutput]=useState(''),[messages,setMessages]=useState([])
  var [unitType,setUnitType]=useState('length'),[from,setFrom]=useState('متر'),[to,setTo]=useState('کیلومتر'),[value,setValue]=useState('')

  function reset(next){setTab(next);setInput('');setOutput('')}
  function runAssistant(mode){if(!input.trim()||busy||!user)return;setBusy(true);var history=messages.slice(-6),question=input.trim();ctx.apiCall('assistant',user.id,question,mode,history).then(function(r){var answer=r&&r.data&&r.data.response;if(answer){setOutput(answer);setMessages(function(items){return items.concat([{role:'user',content:question},{role:'assistant',content:answer}]).slice(-8)})}else ctx.showToast((r&&r.error)||'پاسخی دریافت نشد.','error');setBusy(false)})}
  function runWeather(){if(!input.trim()||busy)return;setBusy(true);ctx.apiCall('weather',input.trim()).then(function(r){var w=r&&r.data;if(w)setOutput(`${w.city}${w.country?'، '+w.country:''}\n${w.condition} • ${w.temperature}°C\nدمای حسی ${w.feels_like}° • رطوبت ${w.humidity}٪ • باد ${w.wind} km/h`);else ctx.showToast((r&&r.error)||'هواشناسی پاسخ نداد.','error');setBusy(false)})}
  function runCalc(){if(!input.trim()||busy)return;setBusy(true);ctx.apiCall('calculate',input.trim()).then(function(r){if(r&&r.data)setOutput(String(r.data.result));else ctx.showToast((r&&r.error)||'عبارت معتبر نیست.','error');setBusy(false)})}
  function convert(){var n=Number(value);if(!Number.isFinite(n))return setOutput('مقدار معتبر وارد کن.');var units=UNITS[unitType].units;setOutput(`${n.toLocaleString('fa-IR')} ${from} = ${(n*units[from]/units[to]).toLocaleString('fa-IR',{maximumFractionDigits:6})} ${to}`)}
  var unitNames=Object.keys(UNITS[unitType].units)
  return <div className="page fade-up">
    <div className="glass" style={{padding:16,marginBottom:12}}><div style={{fontWeight:900,fontSize:18}}>جعبه‌ابزار SectorLand</div><div style={{fontSize:11,color:'var(--muted)',marginTop:5,lineHeight:1.8}}>همه ابزارها همین‌جا اجرا می‌شوند؛ دیگر نیازی به ارسال دستور در چت نیست.</div></div>
    <div style={{display:'flex',gap:7,overflowX:'auto',paddingBottom:12}}>{TABS.map(function(t){return <button key={t[0]} onClick={function(){reset(t[0])}} className="btn btn-sm" style={{flex:'0 0 auto',background:tab===t[0]?'linear-gradient(135deg,var(--accent),var(--accent2))':'var(--card)',color:tab===t[0]?'#fff':'var(--muted)',border:'1px solid var(--border)'}}>{t[1]} {t[2]}</button>})}</div>

    {tab!=='convert'&&<div className="glass" style={{padding:15}}>
      <textarea value={input} onChange={function(e){setInput(e.target.value)}} placeholder={tab==='ai'?'هر سؤالی داری بنویس...':tab==='weather'?'نام شهر؛ مثلاً کرج':tab==='translate'?'متن فارسی یا انگلیسی را وارد کن...':'مثلاً (25 + 5) * 3'} rows={tab==='ai'||tab==='translate'?5:2} style={{width:'100%',resize:'vertical',padding:13,borderRadius:13,border:'1px solid var(--border)',background:'var(--bg)',color:'var(--text)',fontFamily:'inherit',lineHeight:1.8}}/>
      <button className="btn btn-primary" disabled={busy} onClick={tab==='ai'?function(){runAssistant('chat')}:tab==='translate'?function(){runAssistant('translate')}:tab==='weather'?runWeather:runCalc} style={{width:'100%',marginTop:10,padding:13}}>{busy?'⏳ در حال پردازش...':tab==='ai'?'ارسال به Sector AI':tab==='translate'?'ترجمه کن':tab==='weather'?'نمایش وضعیت هوا':'محاسبه'}</button>
    </div>}
    {tab==='convert'&&<div className="glass" style={{padding:15}}>
      <div style={{display:'flex',gap:8,marginBottom:10}}>{Object.keys(UNITS).map(function(k){return <button className="btn btn-sm" key={k} onClick={function(){setUnitType(k);var names=Object.keys(UNITS[k].units);setFrom(names[0]);setTo(names[1]);setOutput('')}} style={{flex:1,background:unitType===k?'var(--accent)':'var(--card)',color:'#fff'}}>{UNITS[k].label}</button>})}</div>
      <input inputMode="decimal" value={value} onChange={function(e){setValue(e.target.value)}} placeholder="مقدار" style={{width:'100%',padding:12,borderRadius:12,border:'1px solid var(--border)',background:'var(--bg)',color:'var(--text)',marginBottom:9}}/>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}><select value={from} onChange={function(e){setFrom(e.target.value)}} style={{padding:11,borderRadius:11,background:'var(--bg)',color:'var(--text)',border:'1px solid var(--border)'}}>{unitNames.map(function(u){return <option key={u}>{u}</option>})}</select><select value={to} onChange={function(e){setTo(e.target.value)}} style={{padding:11,borderRadius:11,background:'var(--bg)',color:'var(--text)',border:'1px solid var(--border)'}}>{unitNames.map(function(u){return <option key={u}>{u}</option>})}</select></div>
      <button className="btn btn-primary" onClick={convert} style={{width:'100%',marginTop:10}}>تبدیل کن</button>
    </div>}
    {output&&<div className="glass" style={{padding:16,marginTop:12,whiteSpace:'pre-wrap',lineHeight:1.9,fontSize:13}}><div style={{fontSize:10,color:'var(--muted)',marginBottom:7}}>نتیجه</div>{output}</div>}
    <div style={{height:20}} />
  </div>
}
