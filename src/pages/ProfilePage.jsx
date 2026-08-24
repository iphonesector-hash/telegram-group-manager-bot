import { useEffect, useState } from 'react'
import Avatar from '../components/ui/Avatar'
import { useAppContext } from '../App'
import SectorRankTrack, {rankFor} from '../components/ui/SectorRankTrack'
import SectorIcon from '../components/ui/SectorIcon'

function memberSince(value) {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleDateString('fa-IR', { year:'numeric', month:'long' })
  } catch (_) { return '—' }
}

export default function ProfilePage() {
  var ctx = useAppContext()
  var tgUser = ctx.tgUser
  var dbUser = ctx.dbUser
  var navigate = ctx.navigate
  var refreshUser = ctx.refreshUser
  var [notif, setNotif] = useState(true)

  useEffect(function() {
    if (refreshUser) refreshUser()
  }, [refreshUser])

  var level = Number(dbUser.level || 1)
  var rank = rankFor(level).title
  var menuItems = [
    { icon: 'orders', label: 'سفارش‌هام', fn: function() { navigate('orders') } },
    { icon: 'referral', label: 'معرفی دوستان', fn: function() { navigate('referral') } },
    { icon: 'trophy', label: 'برترین‌ها', fn: function() { navigate('games') } },
    { icon: 'support', label: 'پشتیبانی', fn: function() { navigate('support') } },
    { icon: 'features', label: 'سایر امکانات ربات', fn: function() { navigate('features') } },
    { icon: 'missions', label: 'ماموریت‌های من', fn: function() { navigate('missions') } },
    { icon: 'sectorpet', label: 'سکتور کوچولوی من', fn: function() { navigate('sectorpet') } },
    { icon: 'settings', label: 'تنظیمات کامل مینی‌اپ', fn: function() { navigate('settings') } },
  ]
  if (dbUser.is_admin) menuItems.unshift({ icon:'admin', label:'پنل مدیریت SectorLand', fn:function(){navigate('admin')} })

  var profileStats = [
    { icon: '🪙', label: 'سکه', val: dbUser.unlimited_wallet ? '∞' : Number(dbUser.coins || 0).toLocaleString() },
    { icon: '⭐', label: 'XP', val: Number(dbUser.xp || 0).toLocaleString() },
    { icon: '📦', label: 'خرید', val: Number(dbUser.orders_count || 0).toLocaleString('fa-IR') },
  ]

  return (
    <div className="page fade-up">
      <div className="glass" style={{padding:0,overflow:'hidden',marginBottom:12,border:'1px solid rgba(112,88,255,.3)'}}>
        <img src="/assets/sector/social-v3/profile.webp" alt="Sector profile" style={{display:'block',width:'100%',maxHeight:190,objectFit:'cover',objectPosition:'center 35%'}} />
      </div>

      <div className="glass" style={{padding:24,textAlign:'center',marginBottom:16,background:'radial-gradient(circle at 50% 0%,rgba(99,77,255,.2),transparent 48%),linear-gradient(135deg,rgba(79,123,255,.14),rgba(162,89,255,.09))'}}>
        <div style={{display:'flex',justifyContent:'center',marginBottom:12}}>
          <div style={{position:'relative',padding:4,borderRadius:'50%',background:'linear-gradient(135deg,#55d8ff,#7d55ff,#ffc857)',boxShadow:'0 0 28px rgba(113,86,255,.28)'}}>
            <div style={{borderRadius:'50%',padding:3,background:'var(--bg)'}}><Avatar user={tgUser} size={80} /></div>
            <div style={{position:'absolute',bottom:1,right:1,background:'linear-gradient(135deg,var(--accent),var(--accent2))',borderRadius:'50%',width:27,height:27,display:'flex',alignItems:'center',justifyContent:'center',fontSize:11,border:'2px solid var(--bg)',fontWeight:900,color:'#fff'}}>{level}</div>
          </div>
        </div>
        <div style={{fontWeight:800,fontSize:20,marginBottom:4}}>{tgUser ? tgUser.first_name : (dbUser.first_name || 'کاربر')} {tgUser && tgUser.last_name ? tgUser.last_name : ''}</div>
        <div style={{fontSize:11,fontWeight:900,color:'#8fdcff',marginBottom:5}}>{rank}</div>
        {dbUser.role && dbUser.role !== 'کاربر' && <div style={{color:'var(--gold)',fontSize:12,fontWeight:900,marginBottom:8}}>👑 {dbUser.role}</div>}
        {tgUser && tgUser.username && <div style={{color:'var(--muted)',fontSize:13,marginBottom:10}}>@{tgUser.username}</div>}
        <div style={{display:'flex',justifyContent:'center',gap:8,flexWrap:'wrap'}}>
          <span className="badge badge-blue">سطح {level.toLocaleString('fa-IR')}</span>
          <span className="badge badge-gold">رتبه #{Number(dbUser.rank || 0).toLocaleString('fa-IR')}</span>
          <span className="badge badge-green">عضو از {memberSince(dbUser.joined_at)}</span>
        </div>
      </div>

      <SectorRankTrack level={level}/>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8,marginBottom:16}}>
        {profileStats.map(function(s,i){return <div key={i} className="stat-pill"><div style={{fontSize:20}}>{s.icon}</div><div style={{fontWeight:800,fontSize:16,marginTop:2}}>{s.val}</div><div style={{fontSize:10,color:'var(--muted)',marginTop:1}}>{s.label}</div></div>})}
      </div>

      <div className="glass" style={{padding:'12px 16px',marginBottom:12}}>
        <div style={{display:'flex',justifyContent:'space-between',padding:'7px 0'}}><span style={{color:'var(--muted)',fontSize:12}}>🏦 موجودی بانک</span><b>{Number(dbUser.bank_balance || 0).toLocaleString()} 🪙</b></div>
        <div style={{display:'flex',justifyContent:'space-between',padding:'7px 0'}}><span style={{color:'var(--muted)',fontSize:12}}>💳 بدهی وام</span><b>{Number(dbUser.loan_balance || 0).toLocaleString()} 🪙</b></div>
      </div>

      <div className="glass" style={{padding:14,marginBottom:12}}>
        <div style={{fontSize:11,color:'var(--muted)',fontWeight:800,marginBottom:10}}>🏅 نشان‌های من</div>
        {(!dbUser.achievements||dbUser.achievements.length===0)&&<div style={{fontSize:11,color:'var(--muted)'}}>اولین نشان هنوز باز نشده؛ یک مسابقه را درست جواب بده.</div>}
        <div style={{display:'flex',gap:8,overflowX:'auto'}}>{(dbUser.achievements||[]).map(function(a){return <div key={a.id||a.title} style={{minWidth:92,textAlign:'center',padding:10,borderRadius:12,background:'linear-gradient(145deg,rgba(112,87,255,.11),rgba(255,255,255,.03))',border:'1px solid rgba(112,87,255,.22)'}}><div style={{fontSize:25}}>{a.icon||'🏅'}</div><div style={{fontSize:9,fontWeight:800,marginTop:5}}>{a.title||a}</div></div>})}</div>
      </div>

      <div className="glass" style={{padding:'10px 16px',marginBottom:12}}><div style={{display:'flex',justifyContent:'space-between',padding:'7px 0'}}><span style={{fontSize:12,color:'var(--muted)'}}>✅ پاسخ درست</span><b>{Number(dbUser.correct_answers||0).toLocaleString('fa-IR')}</b></div><div style={{display:'flex',justifyContent:'space-between',padding:'7px 0'}}><span style={{fontSize:12,color:'var(--muted)'}}>💬 پیام‌های ثبت‌شده</span><b>{Number(dbUser.message_count||0).toLocaleString('fa-IR')}</b></div></div>

      <button onClick={function(){navigate('sectorpet')}} className="glass" style={{display:'flex',alignItems:'center',gap:12,width:'100%',padding:0,overflow:'hidden',marginBottom:12,color:'inherit',border:'1px solid rgba(80,215,255,.22)',cursor:'pointer',textAlign:'right'}}>
        <img src="/assets/sector/koochooloo-moods-v2.webp" alt="Sector Koochooloo" loading="lazy" style={{width:118,height:82,objectFit:'cover',objectPosition:'left center'}} />
        <div style={{flex:1,padding:'10px 0'}}><b style={{fontSize:13}}>🤖 سکتور کوچولوی من</b><div style={{fontSize:10,color:'var(--muted)',marginTop:4}}>مراقبت، بازی، رشد و خاطره‌های مشترک</div></div><span style={{paddingLeft:12,fontSize:20}}>‹</span>
      </button>

      <div className="glass" style={{overflow:'hidden',marginBottom:12}}>
        {menuItems.map(function(item,i){return <button key={i} onClick={item.fn} className="profile-system-row" style={{borderBottom:i<menuItems.length-1?'1px solid var(--border)':'none'}}><i><SectorIcon name={item.icon} size={20}/></i><span>{item.label}</span><b>‹</b></button>})}
      </div>

      <div className="glass" style={{overflow:'hidden'}}>
        <div style={{padding:'10px 16px',borderBottom:'1px solid var(--border)',fontSize:11,color:'var(--muted)',fontWeight:700}}>⚙️ تنظیمات محلی Mini App</div>
        <div style={{display:'flex',alignItems:'center',padding:'14px 16px',borderBottom:'1px solid var(--border)'}}><span style={{flex:1,fontSize:13}}>🔔 اعلان‌های رابط</span><button className={'toggle'+(notif?' on':'')} onClick={function(){setNotif(function(v){return !v})}} /></div>
        <div style={{display:'flex',alignItems:'center',padding:'14px 16px'}}><span style={{flex:1,fontSize:13}}>🆔 شناسه تلگرام</span><span style={{color:'var(--muted)',fontSize:12,fontFamily:'monospace'}}>{tgUser ? tgUser.id : '—'}</span></div>
      </div>
      <div style={{height:16}} />
    </div>
  )
}
