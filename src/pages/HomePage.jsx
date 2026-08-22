import { useEffect, useState } from 'react'
import Avatar from '../components/ui/Avatar'
import { useAppContext } from '../App'

function formatDate(value) {
  if (!value) return '—'
  try { return new Date(value).toLocaleString('fa-IR') } catch (_) { return '—' }
}

export default function HomePage() {
  var ctx = useAppContext()
  var tgUser = ctx.tgUser
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var navigate = ctx.navigate
  var showToast = ctx.showToast
  var apiCall = ctx.apiCall
  var refreshUser = ctx.refreshUser
  var [claiming, setClaiming] = useState(false)
  var [products, setProducts] = useState([])
  var [transactions, setTransactions] = useState([])

  var xp = Number(dbUser.xp || 0)
  var level = Number(dbUser.level || 1)
  var levelStart = Math.max(0, (level - 1) * 100)
  var levelEnd = level * 100
  var xpPct = Math.max(0, Math.min(100, Math.round(((xp - levelStart) / Math.max(1, levelEnd - levelStart)) * 100)))

  useEffect(function() {
    if (!tgUser) return
    Promise.all([apiCall('getShop'), apiCall('getTransactions', tgUser.id)]).then(function(results) {
      var shop = results[0] && results[0].data && Array.isArray(results[0].data.items) ? results[0].data.items : []
      var txs = Array.isArray(results[1] && results[1].data) ? results[1].data : []
      setProducts(shop.slice(0, 4))
      setTransactions(txs.slice(0, 4))
    })
  }, [tgUser, apiCall])

  function handleClaim() {
    if (claiming || !tgUser) return
    setClaiming(true)
    apiCall('dailyClaim', tgUser.id).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'success') {
        setDbUser(function(u) { return { ...u, coins: Number(data.coins || u.coins || 0) } })
        showToast('🎁 ' + Number(data.reward || 0) + ' سکه دریافت شد!', 'success')
        refreshUser()
        apiCall('getTransactions', tgUser.id).then(function(r) {
          setTransactions(Array.isArray(r && r.data) ? r.data.slice(0, 4) : [])
        })
      } else {
        showToast((data && data.message) || 'فعلاً جایزه روزانه در دسترس نیست.', 'error')
      }
      setClaiming(false)
    })
  }

  var quickActions = [
    { icon: '🎁', label: 'هدیه روزانه', sub: 'هر روز سکه بگیر', fn: handleClaim, loading: claiming },
    { icon: '🛒', label: 'فروشگاه', sub: 'خرید با سکه واقعی', fn: function() { navigate('shop') } },
    { icon: '🎮', label: 'بازی و مسابقه', sub: 'سکه و XP بگیر', fn: function() { navigate('games') } },
    { icon: '💰', label: 'بانک', sub: 'واریز، برداشت و وام', fn: function() { navigate('wallet') } },
  ]

  return (
    <div className="page fade-up">
      <div className="glass" style={{padding:'20px',marginBottom:14,background:'linear-gradient(135deg,rgba(79,123,255,.15),rgba(162,89,255,.12))'}}>
        <div style={{display:'flex',alignItems:'center',gap:14,marginBottom:16}}>
          <div style={{position:'relative'}}>
            <Avatar user={tgUser} size={56} />
            <div style={{position:'absolute',bottom:-2,right:-2,background:'var(--accent)',borderRadius:'50%',width:20,height:20,display:'flex',alignItems:'center',justifyContent:'center',fontSize:10,border:'2px solid var(--bg)',fontWeight:700,color:'#fff'}}>{level}</div>
          </div>
          <div style={{flex:1}}>
            <div style={{fontWeight:800,fontSize:18,marginBottom:2}}>سلام، {dbUser.first_name || (tgUser && tgUser.first_name) || 'کاربر'} 👋</div>
            <div style={{color:'var(--muted)',fontSize:12}}>سطح {level} • رتبه {dbUser.rank ? '#' + Number(dbUser.rank).toLocaleString('fa-IR') : '—'}</div>
          </div>
          <div style={{textAlign:'center'}}><div style={{fontWeight:800,fontSize:20,color:'var(--gold)'}}>{Number(dbUser.coins || 0).toLocaleString()}</div><div style={{fontSize:10,color:'var(--muted)'}}>سکه 🪙</div></div>
        </div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'var(--muted)',marginBottom:5}}><span>پیشرفت سطح {level}</span><span>{xp.toLocaleString()} / {levelEnd.toLocaleString()} XP</span></div>
        <div className="progress-bar"><div className="progress-fill" style={{width:xpPct + '%'}} /></div>
      </div>

      <div className="glass" style={{padding:'12px 16px',marginBottom:8,display:'flex',alignItems:'center',gap:10,borderColor:'rgba(34,216,122,.2)'}}><span style={{fontSize:22}}>🔄</span><span style={{fontSize:13}}>این صفحه مستقیماً با حساب ربات SectorLand همگام است.</span></div>

      <div className="sec-title" style={{marginTop:18}}>⚡ دسترسی سریع</div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:20}}>{quickActions.map(function(item,i){return <button key={i} onClick={item.fn} disabled={item.loading} className="glass btn" style={{flexDirection:'column',padding:'18px 10px',gap:6,border:'1px solid var(--border)',cursor:'pointer',textAlign:'center',opacity:item.loading ? 0.6 : 1}}><span style={{fontSize:28}}>{item.loading?'⏳':item.icon}</span><span style={{fontWeight:700,fontSize:13}}>{item.label}</span><span style={{fontSize:11,color:'var(--muted)'}}>{item.sub}</span></button>})}</div>

      <div className="sec-title">🔥 فروشگاه واقعی</div>
      <div className="scroll-row" style={{marginBottom:20}}>
        {products.length === 0 && <div className="glass" style={{padding:16,color:'var(--muted)',fontSize:12}}>محصولی از سرور دریافت نشد.</div>}
        {products.map(function(p){return <div key={p.id} onClick={function(){navigate('shop')}} style={{minWidth:155,flexShrink:0,cursor:'pointer',background:'rgba(79,123,255,.07)',border:'1px solid var(--border)',borderRadius:16,padding:'16px 14px'}}><div style={{fontWeight:700,fontSize:14,marginBottom:8}}>{p.name}</div><div style={{fontWeight:800,fontSize:15,color:'var(--gold)'}}>{Number(p.price || 0).toLocaleString()} 🪙</div><div style={{fontSize:10,color:'var(--muted)',marginTop:4}}>خرید با موجودی ربات</div></div>})}
      </div>

      <div className="sec-title">📋 فعالیت اخیر</div>
      <div className="glass" style={{overflow:'hidden'}}>
        {transactions.length === 0 && <div style={{padding:18,textAlign:'center',color:'var(--muted)',fontSize:12}}>هنوز تراکنشی ثبت نشده.</div>}
        {transactions.map(function(tx,i){var earn=Number(tx.amount)>=0;return <div key={tx.id || i} style={{display:'flex',alignItems:'center',gap:12,padding:'12px 16px',borderBottom:i<transactions.length-1?'1px solid var(--border)':'none'}}><div style={{width:36,height:36,borderRadius:'50%',flexShrink:0,background:earn?'rgba(34,216,122,.12)':'rgba(255,79,106,.12)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:16}}>{earn?'⬆️':'⬇️'}</div><div style={{flex:1}}><div style={{fontSize:13,fontWeight:600}}>{tx.label}</div><div style={{fontSize:11,color:'var(--muted)'}}>{formatDate(tx.date)}</div></div><div style={{fontWeight:700,color:earn?'var(--green)':'var(--red)'}}>{earn?'+':''}{Number(tx.amount || 0).toLocaleString()} 🪙</div></div>})}
      </div>
      <div style={{height:16}} />
    </div>
  )
}
