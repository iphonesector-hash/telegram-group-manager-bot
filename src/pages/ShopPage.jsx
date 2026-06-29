import { useState, useMemo } from 'react'
import Modal from '../components/ui/Modal'
import { MOCK_PRODUCTS } from '../utils/mock'
import { useAppContext } from '../App'

export default function ShopPage() {
  var ctx = useAppContext()
  var tgUser = ctx.tgUser
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var showToast = ctx.showToast
  var apiCall = ctx.apiCall
  var [cat, setCat] = useState('all')
  var [selected, setSelected] = useState(null)
  var [buying, setBuying] = useState(false)

  var cats = [
    { key: 'all',   label: 'همه 🗂️' },
    { key: 'vpn',   label: 'VPN 🔐' },
    { key: 'coins', label: 'سکه 🪙' },
  ]

  var filtered = useMemo(function() {
    return cat === 'all' ? MOCK_PRODUCTS : MOCK_PRODUCTS.filter(function(p) { return p.category === cat })
  }, [cat])

  function handleBuy() {
    if (!selected || buying) return
    setBuying(true)
    apiCall('buyItem', tgUser && tgUser.id, selected.id).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'success') {
        if (data.coins != null) setDbUser(function(u) { return { ...u, coins: data.coins } })
        showToast('✅ خرید موفق: ' + selected.name, 'success')
      } else {
        showToast('❌ خطا در خرید. دوباره تلاش کن.', 'error')
      }
      setBuying(false)
      setSelected(null)
    })
  }

  return (
    <div className="page fade-up">
      <div className="sec-title">🛒 فروشگاه</div>

      {/* Category tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 18, flexWrap: 'wrap' }}>
        {cats.map(function(c) {
          return (
            <button key={c.key} onClick={function() { setCat(c.key) }}
              className="btn btn-sm"
              style={{
                background: cat === c.key ? 'linear-gradient(135deg,var(--accent),var(--accent2))' : 'var(--card)',
                color: cat === c.key ? '#fff' : 'var(--muted)',
                border: cat === c.key ? 'none' : '1px solid var(--border)',
              }}>
              {c.label}
            </button>
          )
        })}
      </div>

      {/* Products */}
      <div style={{ display: 'grid', gap: 12 }}>
        {filtered.map(function(p) {
          return (
            <div key={p.id} className="glass" style={{
              padding: '18px', cursor: 'pointer',
              borderColor: p.badge ? p.color + '30' : 'var(--border)',
              background: 'linear-gradient(135deg,' + p.color + '08,transparent)'
            }} onClick={function() { setSelected(p) }}>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div>
                  {p.badge && (
                    <span className="badge" style={{
                      marginBottom: 6, display: 'inline-block',
                      background: p.color + '20', color: p.color
                    }}>{p.badge}</span>
                  )}
                  <div style={{ fontWeight: 700, fontSize: 16 }}>{p.name}</div>
                  <div style={{ color: 'var(--muted)', fontSize: 12, marginTop: 2 }}>مدت: {p.duration}</div>
                </div>
                <div style={{ textAlign: 'left', flexShrink: 0 }}>
                  {p.coins > 0 && <div style={{ fontSize: 12, color: 'var(--gold)', fontWeight: 600 }}>{p.coins} 🪙</div>}
                  <div style={{ fontWeight: 800, fontSize: 20, color: p.color }}>{p.price.toLocaleString()}</div>
                  <div style={{ fontSize: 10, color: 'var(--muted)' }}>تومان</div>
                </div>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
                {p.features.map(function(f, i) {
                  return (
                    <span key={i} style={{
                      background: 'rgba(255,255,255,.05)', fontSize: 11,
                      padding: '3px 8px', borderRadius: 6, color: 'var(--muted)'
                    }}>✓ {f}</span>
                  )
                })}
              </div>

              <button className="btn btn-primary"
                style={{ background: 'linear-gradient(135deg,' + p.color + ',' + p.color + 'aa)' }}
                onClick={function(e) { e.stopPropagation(); setSelected(p) }}>
                خرید کن
              </button>
            </div>
          )
        })}
      </div>

      {/* Confirm modal */}
      <Modal open={selected !== null} onClose={function() { setSelected(null) }} title="تأیید خرید">
        {selected && (
          <div>
            <div className="glass" style={{
              padding: '16px', marginBottom: 16,
              border: '1px solid ' + selected.color + '33',
              background: 'linear-gradient(135deg,' + selected.color + '10,transparent)'
            }}>
              <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{selected.name}</div>
              <div style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 14 }}>مدت: {selected.duration}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--muted)' }}>مبلغ:</span>
                <span style={{ fontWeight: 800, color: selected.color, fontSize: 18 }}>
                  {selected.price.toLocaleString()} تومان
                </span>
              </div>
            </div>
            <div style={{ color: 'var(--muted)', fontSize: 12, textAlign: 'center', marginBottom: 16 }}>
              اطلاعات اتصال پس از پرداخت به تلگرام ارسال می‌شه
            </div>
            <button className="btn btn-primary" onClick={handleBuy} disabled={buying}
              style={{ marginBottom: 10, background: 'linear-gradient(135deg,' + selected.color + ',' + selected.color + 'bb)' }}>
              {buying ? '⏳ در حال پردازش...' : '✅ تأیید و پرداخت'}
            </button>
            <button className="btn btn-ghost" style={{ width: '100%' }}
              onClick={function() { setSelected(null) }}>
              انصراف
            </button>
          </div>
        )}
      </Modal>
    </div>
  )
}
