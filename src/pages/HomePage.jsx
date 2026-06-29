import { useState } from 'react'
import Avatar from '../components/ui/Avatar'
import { MOCK_PRODUCTS, MOCK_TRANSACTIONS } from '../utils/mock'
import { useAppContext } from '../App'

export default function HomePage() {
  var ctx = useAppContext()
  var tgUser = ctx.tgUser
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var navigate = ctx.navigate
  var showToast = ctx.showToast
  var apiCall = ctx.apiCall
  var [claiming, setClaiming] = useState(false)

  var xpPct = Math.round((dbUser.xp / dbUser.xpNext) * 100)

  function handleClaim() {
    if (claiming) return
    setClaiming(true)
    apiCall('dailyClaim', tgUser && tgUser.id).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'already') {
        showToast('✅ امروز قبلاً هدیه گرفتی!', 'info')
      } else {
        var reward = (data && data.reward) || 50
        var newCoins = (data && data.coins) || (dbUser.coins + reward)
        setDbUser(function(u) { return { ...u, coins: newCoins } })
        showToast('🎁 ' + reward + ' سکه دریافت شد!', 'success')
      }
      setClaiming(false)
    })
  }

  var announcements = [
    { icon: '🚀', text: 'سرورهای جدید اروپا اضافه شدن!' },
    { icon: '🎉', text: 'جشنواره پاییزه — ۲۰٪ تخفیف VPN‌ها' },
  ]

  var quickActions = [
    { icon: '🎁', label: 'هدیه روزانه',  sub: 'هر روز سکه بگیر',   fn: handleClaim, loading: claiming },
    { icon: '🛒', label: 'فروشگاه',      sub: 'خرید VPN و سکه',    fn: function() { navigate('shop') } },
    { icon: '🎰', label: 'گردونه شانس', sub: 'امتحان شانست رو',   fn: function() { navigate('games') } },
    { icon: '👥', label: 'معرفی دوستان', sub: 'کسب درآمد کن',      fn: function() { navigate('referral') } },
  ]

  return (
    <div className="page fade-up">

      {/* Profile card */}
      <div className="glass" style={{
        padding: '20px', marginBottom: 14,
        background: 'linear-gradient(135deg,rgba(79,123,255,.15),rgba(162,89,255,.12))'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
          <div style={{ position: 'relative' }}>
            <Avatar user={tgUser} size={56} />
            <div style={{
              position: 'absolute', bottom: -2, right: -2,
              background: 'var(--accent)', borderRadius: '50%',
              width: 20, height: 20, display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 10,
              border: '2px solid var(--bg)', fontWeight: 700, color: '#fff'
            }}>
              {dbUser.level}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 2 }}>
              سلام، {tgUser ? tgUser.first_name : 'کاربر'} 👋
            </div>
            <div style={{ color: 'var(--muted)', fontSize: 12 }}>
              سطح {dbUser.level} • رتبه #{dbUser.rank}
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontWeight: 800, fontSize: 20, color: 'var(--gold)' }}>
              {dbUser.coins.toLocaleString()}
            </div>
            <div style={{ fontSize: 10, color: 'var(--muted)' }}>سکه 🪙</div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--muted)', marginBottom: 5 }}>
          <span>پیشرفت سطح {dbUser.level}</span>
          <span>{dbUser.xp} / {dbUser.xpNext} XP</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: xpPct + '%' }} />
        </div>
      </div>

      {/* Announcements */}
      {announcements.map(function(a, i) {
        return (
          <div key={i} className="glass" style={{
            padding: '12px 16px', marginBottom: 8,
            display: 'flex', alignItems: 'center', gap: 10,
            borderColor: 'rgba(79,123,255,.2)'
          }}>
            <span style={{ fontSize: 22 }}>{a.icon}</span>
            <span style={{ fontSize: 13 }}>{a.text}</span>
          </div>
        )
      })}

      {/* Quick actions */}
      <div className="sec-title" style={{ marginTop: 18 }}>⚡ دسترسی سریع</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 }}>
        {quickActions.map(function(item, i) {
          return (
            <button key={i} onClick={item.fn} disabled={item.loading}
              className="glass btn"
              style={{
                flexDirection: 'column', padding: '18px 10px', gap: 6,
                border: '1px solid var(--border)', cursor: 'pointer', textAlign: 'center',
                opacity: item.loading ? 0.6 : 1
              }}>
              <span style={{ fontSize: 28 }}>{item.loading ? '⏳' : item.icon}</span>
              <span style={{ fontWeight: 700, fontSize: 13 }}>{item.label}</span>
              <span style={{ fontSize: 11, color: 'var(--muted)' }}>{item.sub}</span>
            </button>
          )
        })}
      </div>

      {/* Featured products */}
      <div className="sec-title">🔥 پیشنهاد ویژه</div>
      <div className="scroll-row" style={{ marginBottom: 20 }}>
        {MOCK_PRODUCTS.filter(function(p) { return p.category === 'vpn' }).map(function(p) {
          return (
            <div key={p.id} onClick={function() { navigate('shop') }}
              style={{
                minWidth: 155, flexShrink: 0, cursor: 'pointer',
                background: 'linear-gradient(135deg,' + p.color + '22,' + p.color + '06)',
                border: '1px solid ' + p.color + '30',
                borderRadius: 16, padding: '16px 14px',
              }}>
              {p.badge && (
                <span className="badge badge-blue" style={{
                  marginBottom: 8, background: p.color + '20', color: p.color
                }}>{p.badge}</span>
              )}
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{p.name}</div>
              <div style={{ color: 'var(--muted)', fontSize: 11, marginBottom: 8 }}>{p.duration}</div>
              <div style={{ fontWeight: 800, fontSize: 15, color: p.color }}>
                {p.price.toLocaleString()} ت
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent activity */}
      <div className="sec-title">📋 فعالیت اخیر</div>
      <div className="glass" style={{ overflow: 'hidden' }}>
        {MOCK_TRANSACTIONS.slice(0, 4).map(function(tx, i) {
          return (
            <div key={tx.id} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '12px 16px',
              borderBottom: i < 3 ? '1px solid var(--border)' : 'none'
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                background: tx.type === 'earn' ? 'rgba(34,216,122,.12)' : 'rgba(255,79,106,.12)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16
              }}>
                {tx.type === 'earn' ? '⬆️' : '⬇️'}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{tx.label}</div>
                <div style={{ fontSize: 11, color: 'var(--muted)' }}>{tx.date}</div>
              </div>
              <div style={{ fontWeight: 700, color: tx.type === 'earn' ? 'var(--green)' : 'var(--red)' }}>
                {tx.amount > 0 ? '+' : ''}{tx.amount} 🪙
              </div>
            </div>
          )
        })}
      </div>
      <div style={{ height: 16 }} />
    </div>
  )
}
