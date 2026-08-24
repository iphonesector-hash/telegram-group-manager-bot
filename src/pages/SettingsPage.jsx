import {useState} from 'react'
import {useAppContext} from '../App'
import SectorIcon from '../components/ui/SectorIcon'

const DEFAULTS={sound:true,soundMode:'full',soundVolume:.8,haptics:true,motion:true,compact:false,dataSaver:false,largeText:false}
function read(){try{return {...DEFAULTS,...JSON.parse(localStorage.getItem('sector-ui-settings')||'{}')}}catch(_){return DEFAULTS}}
function apply(value){const root=document.documentElement;root.dataset.motion=value.motion?'on':'off';root.dataset.compact=value.compact?'on':'off';root.dataset.text=value.largeText?'large':'normal';root.dataset.dataSaver=value.dataSaver?'on':'off';localStorage.setItem('sector-ui-settings',JSON.stringify(value));localStorage.setItem('sector-sound',value.sound?'on':'off')}

export default function SettingsPage(){
 const ctx=useAppContext(),[settings,setSettings]=useState(read)
 function toggle(key){setSettings(v=>{const next={...v,[key]:!v[key]};apply(next);try{ctx.tg?.HapticFeedback?.impactOccurred('light')}catch(_){}return next})}
 function reset(){const next={...DEFAULTS};setSettings(next);apply(next);ctx.showToast('تنظیمات رابط به حالت استاندارد برگشت.','success')}
 function setAudio(key,value){setSettings(v=>{const next={...v,[key]:value};apply(next);return next})}
 const groups=[
  ['صدا و بازخورد',[['sound','صدای دکمه‌ها و رویدادها','sound'],['haptics','لرزش لمسی تلگرام','pulse']]],
  ['ظاهر و حرکت',[['motion','انیمیشن‌ها و آیکون‌های زنده','features'],['compact','چیدمان فشرده','assets'],['largeText','متن خواناتر و بزرگ‌تر','knowledge']]],
  ['مصرف و عملکرد',[['dataSaver','حالت کم‌مصرف تصاویر','charge']]],
 ]
 return <div className="page fade-up"><section className="settings-hero glass"><div className="settings-core"><img src="/assets/sector/sector-core-logo-v1.webp" alt="Sector Core"/><i/></div><div><small>SYSTEM CONTROL</small><h2>تنظیمات مینی‌اپ</h2><p>ظاهر، صدا، حرکت و مصرف داده را از یک مرکز کنترل کن.</p></div></section><section className="settings-group glass"><h3>حالت صدای سکتور</h3><div className="settings-audio-mode"><button className={settings.soundMode==="full"?"active":""} onClick={()=>setAudio("soundMode","full")}>کامل و سینمایی</button><button className={settings.soundMode==="calm"?"active":""} onClick={()=>setAudio("soundMode","calm")}>آرام و کم‌صدا</button></div><label className="settings-volume"><span>شدت صدا</span><input type="range" min="0.2" max="1" step="0.1" value={settings.soundVolume} onChange={e=>setAudio("soundVolume",Number(e.target.value))}/><b>{Math.round(settings.soundVolume*100)}٪</b></label></section>{groups.map(([title,items])=><section className="settings-group glass" key={title}><h3>{title}</h3>{items.map(([key,label,icon])=><button key={key} onClick={()=>toggle(key)}><i><SectorIcon name={icon} size={17}/></i><span>{label}</span><b className={`toggle${settings[key]?' on':''}`}/></button>)}</section>)}<section className="settings-group glass"><h3>مدیریت برنامه</h3><button onClick={()=>window.location.replace(window.location.pathname+'?refresh='+Date.now())}><i><SectorIcon name="refresh" size={17}/></i><span>دریافت آخرین نسخه</span><em>اجرا</em></button><button onClick={reset}><i><SectorIcon name="repair" size={17}/></i><span>بازنشانی تنظیمات محلی</span><em>بازنشانی</em></button>{ctx.dbUser?.is_admin?<button onClick={()=>ctx.navigate('admin')}><i><SectorIcon name="admin" size={17}/></i><span>تنظیمات مدیریتی و اقتصاد</span><em>ورود</em></button>:null}</section></div>
}
