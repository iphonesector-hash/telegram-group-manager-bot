import {useState} from 'react'
import {useAppContext} from '../App'

const DEFAULTS={sound:true,haptics:true,motion:true,compact:false,dataSaver:false,largeText:false}
function read(){try{return {...DEFAULTS,...JSON.parse(localStorage.getItem('sector-ui-settings')||'{}')}}catch(_){return DEFAULTS}}
function apply(value){const root=document.documentElement;root.dataset.motion=value.motion?'on':'off';root.dataset.compact=value.compact?'on':'off';root.dataset.text=value.largeText?'large':'normal';root.dataset.dataSaver=value.dataSaver?'on':'off';localStorage.setItem('sector-ui-settings',JSON.stringify(value));localStorage.setItem('sector-sound',value.sound?'on':'off')}

export default function SettingsPage(){
 const ctx=useAppContext(),[settings,setSettings]=useState(read)
 function toggle(key){setSettings(v=>{const next={...v,[key]:!v[key]};apply(next);try{ctx.tg?.HapticFeedback?.impactOccurred('light')}catch(_){}return next})}
 function reset(){const next={...DEFAULTS};setSettings(next);apply(next);ctx.showToast('تنظیمات رابط به حالت استاندارد برگشت.','success')}
 const groups=[
  ['صدا و بازخورد',[['sound','صدای دکمه‌ها و رویدادها','🔊'],['haptics','لرزش لمسی تلگرام','〰️']]],
  ['ظاهر و حرکت',[['motion','انیمیشن‌ها و آیکون‌های زنده','✦'],['compact','چیدمان فشرده','▦'],['largeText','متن خواناتر و بزرگ‌تر','Aa']]],
  ['مصرف و عملکرد',[['dataSaver','حالت کم‌مصرف تصاویر','◫']]],
 ]
 return <div className="page fade-up"><section className="settings-hero glass"><img src="/assets/sector/sector-core-logo-v1.webp" alt="Sector Core"/><div><small>SYSTEM CONTROL</small><h2>تنظیمات مینی‌اپ</h2><p>ظاهر، صدا، حرکت و مصرف داده را از یک مرکز کنترل کن.</p></div></section>{groups.map(([title,items])=><section className="settings-group glass" key={title}><h3>{title}</h3>{items.map(([key,label,icon])=><button key={key} onClick={()=>toggle(key)}><i>{icon}</i><span>{label}</span><b className={`toggle${settings[key]?' on':''}`}/></button>)}</section>)}<section className="settings-group glass"><h3>مدیریت برنامه</h3><button onClick={()=>window.location.replace(window.location.pathname+'?refresh='+Date.now())}><i>↻</i><span>دریافت آخرین نسخه</span><em>اجرا</em></button><button onClick={reset}><i>⌫</i><span>بازنشانی تنظیمات محلی</span><em>بازنشانی</em></button>{ctx.dbUser?.is_admin?<button onClick={()=>ctx.navigate('admin')}><i>♛</i><span>تنظیمات مدیریتی و اقتصاد</span><em>ورود</em></button>:null}</section></div>
}
