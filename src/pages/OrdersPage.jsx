import { useEffect, useState } from 'react'
import EmptyState from '../components/ui/EmptyState'
import { useAppContext } from '../App'

function OrderCard({ order }) {
  var created = order.created_at ? new Date(order.created_at).toLocaleString('fa-IR') : '—'
  return (
    <div className="glass" style={{padding:16,marginBottom:10}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
        <div style={{fontWeight:700,fontSize:15}}>{order.name || 'سفارش SectorLand'}</div>
        <span className="badge badge-green">✅ ثبت شده</span>
      </div>
      <div style={{fontSize:12,color:'var(--muted)',lineHeight:1.9}}>🧾 شناسه سفارش: {order.id}<br/>🪙 مبلغ: {Number(order.amount || 0).toLocaleString()} سکه<br/>📅 زمان ثبت: {created}</div>
    </div>
  )
}

export default function OrdersPage() {
  var ctx = useAppContext()
  var navigate = ctx.navigate
  var apiCall = ctx.apiCall
  var tgUser = ctx.tgUser
  var [orders, setOrders] = useState([])
  var [loading, setLoading] = useState(true)

  useEffect(function() {
    if (!tgUser) { setLoading(false); return }
    setLoading(true)
    apiCall('getOrders', tgUser.id).then(function(result) {
      setOrders(Array.isArray(result && result.data) ? result.data : [])
      setLoading(false)
    })
  }, [tgUser, apiCall])

  return (
    <div className="page fade-up">
      <div className="sec-title">📦 سفارش‌های من</div>
      {loading && <div className="glass" style={{padding:20,textAlign:'center',color:'var(--muted)'}}>در حال دریافت سفارش‌های واقعی...</div>}
      {!loading && orders.length === 0 && <EmptyState icon="📦" title="هنوز سفارشی ثبت نشده" sub="خریدهای ثبت‌شده با حساب ربات اینجا نمایش داده می‌شن." action="رفتن به فروشگاه" onAction={function(){navigate('shop')}} />}
      {!loading && orders.map(function(order){return <OrderCard key={order.id} order={order} />})}
    </div>
  )
}
