import { useEffect, useState } from 'react'
import { useAppContext } from '../App'

const FIELDS = [
  ['vpn_price_1m','VPN یک‌ماهه','🪙'],['vpn_price_3m','VPN سه‌ماهه','🪙'],['vpn_price_6m','VPN شش‌ماهه','🪙'],
  ['daily_reward','جایزه روزانه','🪙'],['vip_daily_reward','جایزه روزانه VIP','🪙'],
  ['wheel_cooldown_hours','فاصله گردونه','ساعت'],['referral_reward','جایزه دعوت','🪙'],
]

export default function AdminPage() {
  var ctx = useAppContext()
  var [data,setData] = useState(null)
  var [settings,setSettings] = useState({})
  var [saving,setSaving] = useState(false)

  useEffect(function(){
    ctx.apiCall('getAdminOverview').then(function(r){
      if (r && r.data) { setData(r.data); setSettings(r.data.settings || {}) }
      else ctx.showToast('دسترسی پنل مدیریت تأیید نشد.','error')
    })
  },[ctx.apiCall,ctx.showToast])

  function save() {
    if (saving) return
    setSaving(true)
    ctx.apiCall('updateAdminSettings',settings).then(function(r){
      if (r && r.data && r.data.status === 'success') {
        setSettings(r.data.settings || settings)
        ctx.showToast('تنظیمات با موفقیت ذخیره شد.','success')
      } else ctx.showToast((r && r.error) || 'ذخیره تنظیمات انجام نشد.','error')
      setSaving(false)
    })
  }

  if (!ctx.dbUser.is_admin) return <div className="page"><div className="glass" style={{padding:24,textAlign:'center'}}>🔒 این بخش فقط برای مدیر اصلی است.</div></div>
  if (!data) return <div className="page"><div className="glass" style={{padding:24,textAlign:'center'}}>⏳ در حال دریافت وضعیت سامانه...</div></div>

  var stats=[['👥','کاربران',data.users],['🏢','گروه‌های فعال',data.groups],['🧾','تراکنش ۲۴ ساعت',data.purchases_24h],['🪙','سکه کاربران',data.coins_in_wallets]]
  return <div className="page fade-up">
    <div className="glass" style={{padding:18,marginBottom:14,background:'linear-gradient(135deg,rgba(255,180,40,.14),rgba(112,72,255,.12))'}}>
      <div style={{fontSize:11,color:'var(--gold)',fontWeight:900}}>COMMAND CENTER</div>
      <div style={{fontWeight:900,fontSize:20,marginTop:5}}>پنل مدیریت SectorLand</div>
      <div style={{fontSize:11,color:'var(--muted)',marginTop:5}}>تنظیمات حساس فقط پس از اعتبارسنجی امضای تلگرام ذخیره می‌شوند.</div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9,marginBottom:16}}>{stats.map(function(s){return <div className="glass" key={s[1]} style={{padding:14}}><div style={{fontSize:22}}>{s[0]}</div><div style={{fontWeight:900,fontSize:19,marginTop:5}}>{Number(s[2]||0).toLocaleString('fa-IR')}</div><div style={{fontSize:10,color:'var(--muted)'}}>{s[1]}</div></div>})}</div>
    <div className="sec-title">⚙️ تنظیمات زنده</div>
    <div className="glass" style={{padding:14,marginBottom:12}}>
      {FIELDS.map(function(field){return <label key={field[0]} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:'1px solid var(--border)'}}><span style={{flex:1,fontSize:12}}>{field[1]}</span><input inputMode="numeric" value={settings[field[0]] == null ? '' : settings[field[0]]} onChange={function(e){var value=e.target.value.replace(/\D/g,'');setSettings(function(v){return {...v,[field[0]]:Number(value||0)}})}} style={{width:100,padding:'9px 10px',borderRadius:10,border:'1px solid var(--border)',background:'var(--bg)',color:'var(--text)',textAlign:'center'}}/><small style={{width:35,color:'var(--muted)'}}>{field[2]}</small></label>})}
      <label style={{display:'flex',alignItems:'center',padding:'13px 0 4px'}}><span style={{flex:1,fontSize:12}}>حالت تعمیر فروشگاه</span><button className={'toggle'+(settings.maintenance_mode?' on':'')} onClick={function(){setSettings(function(v){return {...v,maintenance_mode:!v.maintenance_mode}})}} /></label>
      <label style={{display:'flex',alignItems:'center',padding:'13px 0 4px'}}><span style={{flex:1,fontSize:12}}>تورنمنت هفتگی</span><button className={'toggle'+(settings.weekly_tournament_enabled?' on':'')} onClick={function(){setSettings(function(v){return {...v,weekly_tournament_enabled:!v.weekly_tournament_enabled}})}} /></label>
    </div>
    <button className="btn btn-primary" disabled={saving} onClick={save} style={{width:'100%',padding:14}}>{saving?'⏳ در حال ذخیره...':'💾 ذخیره تنظیمات'}</button>
    <div style={{height:20}} />
  </div>
}
