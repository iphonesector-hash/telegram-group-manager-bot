import {ShopItemArt} from './SectorVisuals'

const COLORS=['#5edcff','#697cff','#a76cff','#ff5f78','#ffb447','#56e2a4','#e8edf5','#202a3d']

export default function SectorRobotWorkshop({pet,shop,onColor,onEquip,busy}){
  const appearance=pet?.appearance||{}
  const equipped=shop.filter(x=>x.owned&&x.equipped)
  const primary=appearance.primary_color||'#637cff',secondary=appearance.secondary_color||'#b9c8dc',core=appearance.core_color||'#5fe6ff'
  const mood=Number(pet?.energy||0)<25?'low':Number(pet?.health||0)<30?'damaged':Number(pet?.hunger||0)<30?'hungry':Number(pet?.happiness||0)>80?'happy':'stable'
  const status={low:'شارژم رو به اتمامه؛ به ایستگاه انرژی نیاز دارم.',damaged:'زره آسیب دیده؛ قبل از مأموریت من را تعمیر کن.',hungry:'سوخت غذایی کمه؛ برای ادامه مسیر غذا لازم دارم.',happy:'همه سامانه‌ها عالی‌اند؛ آماده مأموریت بعدی‌ام.',stable:'سامانه‌ها پایدارند؛ فرمان بعدی را از مرکز مأموریت بگیر.'}[mood]
  return <section className="sector-workshop">
    <header><div><small>MY SECTOR WORKSHOP</small><h3>سکتور من</h3><p>رنگ و قطعات خریداری‌شده را روی ربات شخصی خودت فعال کن.</p></div><span>Lv.{pet?.level||1}</span></header>
    <div className="sector-workshop__stats"><span><small>قدرت</small><b>{pet?.equipment_stats?.power||0}</b></span><span><small>زره</small><b>{pet?.equipment_stats?.defense||0}</b></span><span><small>ذخیره انرژی</small><b>+{pet?.equipment_stats?.energy_bonus||0}</b></span><span><small>رده تجهیزات</small><b>{pet?.equipment_stats?.tier||1}</b></span></div>
    <div className={`sector-workshop__stage sector-workshop__stage--${mood}`} style={{'--robot-primary':primary,'--robot-secondary':secondary,'--robot-core':core}}>
      <div className="sector-workshop__speech">{status}</div>
      <div className={`sector-layerbot sector-layerbot--${mood}`} role="img" aria-label="ربات شخصی‌سازی‌شده کاربر"><i className="antenna"/><div className="head"><div className="visor"><i/><i/></div></div><div className="body"><i className="core"/></div><i className="arm arm--r"/><i className="arm arm--l"/><i className="leg leg--r"/><i className="leg leg--l"/>{mood==='damaged'?<i className="sector-sparks"/>:null}</div>
      {equipped.filter(x=>x.slot!=='background').map(x=><div key={x.id} className={'sector-workshop__equipped slot--'+x.slot} title={x.title}><ShopItemArt item={x} size={54}/><span>{x.title}</span></div>)}
    </div>
    <div className="sector-color-lab"><b>رنگ بدنه</b><div>{COLORS.map(c=><button key={c} aria-label={'انتخاب رنگ '+c} className={primary===c?'active':''} style={{background:c}} onClick={()=>onColor('primary_color',c)}/>)}</div><b>نور هسته</b><div>{COLORS.slice(0,6).map(c=><button key={c} aria-label={'رنگ هسته '+c} className={core===c?'active':''} style={{background:c}} onClick={()=>onColor('core_color',c)}/>)}</div></div>
    <div className="sector-workshop__owned"><div><b>قطعات قابل استفاده</b><span>{shop.filter(x=>x.owned).length} دارایی</span></div><div>{shop.filter(x=>x.owned).slice(0,12).map(x=><button key={x.id} disabled={busy||x.equipped} className={x.equipped?'active':''} onClick={()=>onEquip(x)}><ShopItemArt item={x} size={64}/><span>{x.equipped?'فعال':x.title}</span><small>قدرت +{x.power||0} · زره +{x.defense||0}</small></button>)}</div></div>
  </section>
}
