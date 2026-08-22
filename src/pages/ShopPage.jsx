import { useEffect, useMemo, useState } from 'react'
import Modal from '../components/ui/Modal'
import { useAppContext } from '../App'

function decorateProduct(item, index) {
  var id = Number(item && item.id)
  var name = (item && item.name) || 'محصول SectorLand'
  var price = Number((item && item.price) || 0)
  var isVpn = /vpn/i.test(name)
  return {
    id: id,
    name: name,
    price: price,
    category: isVpn ? 'vpn' : 'extras',
    duration: isVpn ? (id === 2 ? '۳ ماه' : '۱ ماه') : '—',
    features: isVpn
      ? ['فعال‌سازی روی حساب واقعی ربات', 'ثبت خرید در تراکنش‌ها', 'تحویل از طریق SectorLand']
      : ['خرید با سکه حساب ربات', 'ثبت فوری در تاریخچه'],
    badge: index === 0 ? 'پیشنهاد' : '',
  }
}

export default function ShopPage() {
  var ctx = useAppContext()
  var tgUser = ctx.tgUser
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var showToast = ctx.showToast
  var apiCall = ctx.apiCall
  var refreshUser = ctx.refreshUser
  var [cat, setCat] = useState('all')
  var [selected, setSelected] = useState(null)
  var [buying, setBuying] = useState(false)
  var [products, setProducts] = useState([])
  var [loading, setLoading] = useState(true)

  useEffect(function() {
    setLoading(true)
    apiCall('getShop').then(function(result) {
      var raw = result && result.data && Array.isArray(result.data.items) ? result.data.items : []
      setProducts(raw.map(decorateProduct))
      if (!raw.length) showToast('فروشگاه از سرور دریافت نشد.', 'error')
      setLoading(false)
    })
  }, [apiCall, showToast])

  var cats = [
    { key: 'all', label: 'همه 🗂️' },
    { key: 'vpn', label: 'VPN 🔐' },
    { key: 'extras', label: 'سایر 🎁' },
  ]

  var filtered = useMemo(function() {
    return cat === 'all' ? products : products.filter(function(p) { return p.category === cat })
  }, [cat, products])

  function handleBuy() {
    if (!selected || buying || !tgUser) return
    setBuying(true)
    apiCall('buyItem', tgUser.id, selected.id).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'success') {
        if (data.coins != null) setDbUser(function(u) { return { ...u, coins: Number(data.coins) } })
        showToast('✅ خرید موفق: ' + selected.name, 'success')
        refreshUser()
      } else {
        showToast((data && data.message) || '❌ خرید انجام نشد.', 'error')
      }
      setBuying(false)
      setSelected(null)
    })
  }

  return (
    <div className="page fade-up">
      <div className="sec-title">🛒 فروشگاه</div>
      <div className="glass" style={{padding:'10px 14px',marginBottom:14,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <span style={{fontSize:12,color:'var(--muted)'}}>موجودی حساب واقعی</span>
        <span style={{fontWeight:800,color:'var(--gold)'}}>{Number(dbUser.coins || 0).toLocaleString()} 🪙</span>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 18, flexWrap: 'wrap' }}>
        {cats.map(function(c) {
          return <button key={c.key} onClick={function() { setCat(c.key) }} className="btn btn-sm" style={{background:cat===c.key?'linear-gradient(135deg,var(--accent),var(--accent2))':'var(--card)',color:cat===c.key?'#fff':'var(--muted)',border:cat===c.key?'none':'1px solid var(--border)'}}>{c.label}</button>
        })}
      </div>

      {loading && <div className="glass" style={{padding:20,textAlign:'center',color:'var(--muted)'}}>در حال دریافت فروشگاه واقعی...</div>}
      {!loading && filtered.length === 0 && <div className="glass" style={{padding:20,textAlign:'center',color:'var(--muted)'}}>محصولی در این بخش وجود ندارد.</div>}

      <div style={{ display: 'grid', gap: 12 }}>
        {!loading && filtered.map(function(p) {
          return (
            <div key={p.id} className="glass" style={{padding:'18px',cursor:'pointer',borderColor:p.badge?'rgba(79,123,255,.28)':'var(--border)'}} onClick={function() { setSelected(p) }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:12 }}>
                <div>
                  {p.badge && <span className="badge badge-blue" style={{marginBottom:6,display:'inline-block'}}>{p.badge}</span>}
                  <div style={{fontWeight:700,fontSize:16}}>{p.name}</div>
                  <div style={{color:'var(--muted)',fontSize:12,marginTop:2}}>مدت: {p.duration}</div>
                </div>
                <div style={{textAlign:'left',flexShrink:0}}>
                  <div style={{fontWeight:800,fontSize:20,color:'var(--gold)'}}>{p.price.toLocaleString()}</div>
                  <div style={{fontSize:10,color:'var(--muted)'}}>سکه 🪙</div>
                </div>
              </div>
              <div style={{display:'flex',flexWrap:'wrap',gap:6,marginBottom:14}}>{p.features.map(function(f,i){return <span key={i} style={{background:'rgba(255,255,255,.05)',fontSize:11,padding:'3px 8px',borderRadius:6,color:'var(--muted)'}}>✓ {f}</span>})}</div>
              <button className="btn btn-primary" onClick={function(e) { e.stopPropagation(); setSelected(p) }}>خرید با سکه</button>
            </div>
          )
        })}
      </div>

      <Modal open={selected !== null} onClose={function() { setSelected(null) }} title="تأیید خرید">
        {selected && <div>
          <div className="glass" style={{padding:'16px',marginBottom:16}}>
            <div style={{fontWeight:700,fontSize:16,marginBottom:4}}>{selected.name}</div>
            <div style={{color:'var(--muted)',fontSize:13,marginBottom:14}}>این خرید روی همان حساب تلگرام ثبت می‌شود.</div>
            <div style={{display:'flex',justifyContent:'space-between'}}><span style={{color:'var(--muted)'}}>هزینه:</span><span style={{fontWeight:800,color:'var(--gold)',fontSize:18}}>{selected.price.toLocaleString()} 🪙</span></div>
          </div>
          <button className="btn btn-primary" onClick={handleBuy} disabled={buying || Number(dbUser.coins || 0) < selected.price} style={{marginBottom:10}}>{buying?'⏳ در حال ثبت...':Number(dbUser.coins || 0) < selected.price?'سکه کافی نیست':'✅ تأیید خرید'}</button>
          <button className="btn btn-ghost" style={{width:'100%'}} onClick={function() { setSelected(null) }}>انصراف</button>
        </div>}
      </Modal>
    </div>
  )
}
