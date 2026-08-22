import { useEffect, useState } from 'react'
import Avatar from '../components/ui/Avatar'
import { useAppContext } from '../App'

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

  var menuItems = [
    { icon: '📦', label: 'سفارش‌هام', fn: function() { navigate('orders') } },
    { icon: '👥', label: 'معرفی دوستان', fn: function() { navigate('referral') } },
    { icon: '🏆', label: 'برترین‌ها', fn: function() { navigate('games') } },
    { icon: '❓', label: 'پشتیبانی', fn: function() { navigate('support') } },
  ]

  var profileStats = [
    { icon: '🪙', label: 'سکه', val: Number(dbUser.coins || 0).toLocaleString() },
    { icon: '⭐', label: 'XP', val: Number(dbUser.xp || 0).toLocaleString() },
    { icon: '📦', label: 'خرید', val: Number(dbUser.orders_count || 0).toLocaleString('fa-IR') },
  ]

  return (
    <div className="page fade-up">
      <div className="glass" style={{padding:24,textAlign:'center',marginBottom:16,background:'linear-gradient(135deg,rgba(79,123,255,.15),rgba(162,89,255,.1))'}}>
        <div style={{display:'flex',justifyContent:'center',marginBottom:12}}>
          <div style={{position:'relative'}}>
            <Avatar user={tgUser} size={80} />
            <div style={{position:'absolute',bottom:0,right:0,background:'var(--accent)',borderRadius:'50%',width:24,height:24,display:'flex',alignItems:'center',justifyContent:'center',fontSize:11,border:'2px solid var(--bg)',fontWeight:700,color:'#fff'}}>{Number(dbUser.level || 1)}</div>
          </div>
        </div>
        <div style={{fontWeight:800,fontSize:20,marginBottom:4}}>{tgUser ? tgUser.first_name : (dbUser.first_name || 'کاربر')} {tgUser && tgUser.last_name ? tgUser.last_name : ''}</div>
        {tgUser && tgUser.username && <div style={{color:'var(--muted)',fontSize:13,marginBottom:10}}>@{tgUser.username}</div>}
        <div style={{display:'flex',justifyContent:'center',gap:8,flexWrap:'wrap'}}>
          <span className="badge badge-blue">سطح {Number(dbUser.level || 1).toLocaleString('fa-IR')}</span>
          <span className="badge badge-gold">رتبه #{Number(dbUser.rank || 0).toLocaleString('fa-IR')}</span>
          <span className="badge badge-green">عضو از {memberSince(dbUser.joined_at)}</span>
        </div>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8,marginBottom:16}}>
        {profileStats.map(function(s,i){return <div key={i} className="stat-pill"><div style={{fontSize:20}}>{s.icon}</div><div style={{fontWeight:800,fontSize:16,marginTop:2}}>{s.val}</div><div style={{fontSize:10,color:'var(--muted)',marginTop:1}}>{s.label}</div></div>})}
      </div>

      <div className="glass" style={{padding:'12px 16px',marginBottom:12}}>
        <div style={{display:'flex',justifyContent:'space-between',padding:'7px 0'}}><span style={{color:'var(--muted)',fontSize:12}}>🏦 موجودی بانک</span><b>{Number(dbUser.bank_balance || 0).toLocaleString()} 🪙</b></div>
        <div style={{display:'flex',justifyContent:'space-between',padding:'7px 0'}}><span style={{color:'var(--muted)',fontSize:12}}>💳 بدهی وام</span><b>{Number(dbUser.loan_balance || 0).toLocaleString()} 🪙</b></div>
      </div>

      <div className="glass" style={{overflow:'hidden',marginBottom:12}}>
        {menuItems.map(function(item,i){return <button key={i} onClick={item.fn} style={{display:'flex',alignItems:'center',gap:14,padding:'14px 16px',width:'100%',background:'transparent',border:'none',borderBottom:i<menuItems.length-1?'1px solid var(--border)':'none',color:'var(--text)',cursor:'pointer',textAlign:'right',fontFamily:'Vazirmatn, sans-serif'}}><span style={{fontSize:20}}>{item.icon}</span><span style={{flex:1,fontSize:14,fontWeight:500}}>{item.label}</span><span style={{color:'var(--muted)',fontSize:18}}>‹</span></button>})}
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
