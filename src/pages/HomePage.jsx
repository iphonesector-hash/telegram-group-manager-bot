import { useEffect, useState } from 'react'
import Avatar from '../components/ui/Avatar'
import SectorCelebration from '../components/ui/SectorCelebration'
import { useAppContext } from '../App'
import SectorRankTrack, {rankFor} from '../components/ui/SectorRankTrack'

function formatDate(value) {
  if (!value) return '—'
  try { return new Date(value).toLocaleString('fa-IR') } catch (_) { return '—' }
}

function rankName(level) { return rankFor(level).title }

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
  var [celebration, setCelebration] = useState(null)

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
    var beforeLevel = level
    var beforeRank = rankName(beforeLevel)
    setClaiming(true)
    apiCall('dailyClaim', tgUser.id).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'success') {
        var reward = Number(data.reward || 0)
        setDbUser(function(u) { return { ...u, coins: Number(data.coins || u.coins || 0) } })
        showToast('🎁 ' + reward + ' سکه دریافت شد!', 'success')
        refreshUser().then(function(updated) {
          var nextLevel = Number(updated && updated.level || beforeLevel)
          var nextRank = rankName(nextLevel)
          var leveled = nextLevel > beforeLevel
          var ranked = nextRank !== beforeRank
          setCelebration({
            title: ranked ? '🏆 RANK UP!' : leveled ? '⚡ LEVEL UP!' : '🎁 هدیه روزانه',
            text: ranked
              ? '+' + reward + ' سکه گرفتی و به ' + nextRank + ' رسیدی!'
              : leveled
                ? '+' + reward + ' سکه گرفتی و سطح ' + nextLevel + ' شدی!'
                : '+' + reward + ' سکه مستقیم روی حساب SectorLand ثبت شد.'
          })
        })
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
    { icon: '🤖', label: 'سکتور کوچولو', sub: 'همراه هوشمندت را بزرگ کن', fn: function() { navigate('sectorpet') } },
    { icon: '🎁', label: 'هدیه روزانه', sub: 'هر روز سکه بگیر', fn: handleClaim, loading: claiming },
    { icon: '🎯', label: 'ماموریت‌ها', sub: 'سکه و XP جایزه بگیر', fn: function() { navigate('missions') } },
    { icon: '🛒', label: 'فروشگاه', sub: 'خرید با سکه واقعی', fn: function() { navigate('shop') } },
    { icon: '🎡', label: 'گردونه و بازی', sub: 'جایزه و بازی‌های جدید', fn: function() { navigate('games') } },
    { icon: '💰', label: 'بانک', sub: 'واریز، برداشت و وام', fn: function() { navigate('wallet') } },
    { icon: '🌐', label: 'سایر امکانات', sub: 'مدیریت، ابزار و سرگرمی', fn: function() { navigate('features') } },
    { icon: '👤', label: 'پروفایل من', sub: 'حساب و سوابق واقعی', fn: function() { navigate('profile') } },
  ]

  return (
    <div className="page fade-up">
      <button onClick={function(){navigate('sectorpet')}} className="glass" style={{display:'block',width:'100%',padding:0,marginBottom:12,overflow:'hidden',border:'1px solid rgba(125,92,255,.35)',cursor:'pointer',textAlign:'inherit',color:'inherit',background:'#090c27'}}>
        <img src="/assets/sector/koochooloo-hero-v2.webp" alt="Sector Koochooloo" fetchPriority="high" style={{display:'block',width:'100%',aspectRatio:'1.32',objectFit:'cover',objectPosition:'center 42%'}} />
        <div style={{padding:'10px 14px',display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><b style={{fontSize:13}}>💙 سکتور کوچولو، همراه همیشگی تو</b><div style={{fontSize:10,color:'var(--muted)',marginTop:3}}>بازی کن • رشد کن • جایزه بگیر</div></div>
          <span style={{fontSize:18}}>‹</span>
        </div>
      </button>

      <div className="glass" style={{padding:'20px',marginBottom:14,background:'linear-gradient(135deg,rgba(79,123,255,.15),rgba(162,89,255,.12))'}}>
        <div style={{display:'flex',alignItems:'center',gap:14,marginBottom:16}}>
          <div style={{position:'relative'}}>
            <Avatar user={tgUser} size={56} />
            <div style={{position:'absolute',bottom:-2,right:-2,background:'var(--accent)',borderRadius:'50%',width:20,height:20,display:'flex',alignItems:'center',justifyContent:'center',fontSize:10,border:'2px solid var(--bg)',fontWeight:700,color:'#fff'}}>{level}</div>
          </div>
          <div style={{flex:1}}>
            <div style={{fontWeight:800,fontSize:18,marginBottom:2}}>سلام، {dbUser.first_name || (tgUser && tgUser.first_name) || 'کاربر'} 👋</div>
            <div style={{color:'var(--muted)',fontSize:12}}>سطح {level} • {rankName(level)} • رتبه {dbUser.rank ? '#' + Number(dbUser.rank).toLocaleString('fa-IR') : '—'}</div>
          </div>
          <div style={{textAlign:'center'}}><div style={{fontWeight:800,fontSize:20,color:'var(--gold)'}}>{dbUser.unlimited_wallet?'∞':Number(dbUser.coins || 0).toLocaleString()}</div><div style={{fontSize:10,color:'var(--muted)'}}>سکه 🪙</div></div>
        </div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'var(--muted)',marginBottom:5}}><span>پیشرفت سطح {level}</span><span>{xp.toLocaleString()} / {levelEnd.toLocaleString()} XP</span></div>
        <div className="progress-bar"><div className="progress-fill" style={{width:xpPct + '%'}} /></div>
      </div>

      <div className="glass" style={{padding:0,overflow:'hidden',marginBottom:10}}>
        <img src="/assets/sector/koochooloo-moods-v2.webp" alt="حالت‌های سکتور کوچولو" loading="lazy" style={{display:'block',width:'100%',aspectRatio:'3/1',objectFit:'cover'}} />
      </div>

      <SectorRankTrack level={level}/>

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
        {transactions.map(function(tx,i){var earn=Number(tx.amount)>=0;return <div key={tx.id || i} style={{display:'flex',alignItems:'center',gap:12,padding:'12px 16px',borderBottom:i<transactions.length-1?'1px solid var(--border)':'none'}}><div style={{width:42,height:42,borderRadius:'13px',flexShrink:0,background:earn?'rgba(34,216,122,.12)':'rgba(255,79,106,.12)',display:'grid',placeItems:'center',fontSize:10,color:earn?'var(--green)':'var(--red)'}}>{tx.direction|| (earn?'ورودی':'خروجی')}</div><div style={{flex:1}}><div style={{fontSize:13,fontWeight:600}}>{tx.label}</div><div style={{fontSize:11,color:'var(--muted)'}}>{formatDate(tx.date)}</div></div><div style={{fontWeight:700,color:earn?'var(--green)':'var(--red)'}}>{earn?'+':''}{Number(tx.amount || 0).toLocaleString('fa-IR')} سکه</div></div>})}
      </div>
      <SectorCelebration open={!!celebration} title={celebration&&celebration.title} text={celebration&&celebration.text} onClose={function(){setCelebration(null)}} />
      <div style={{height:16}} />
    </div>
  )
}
