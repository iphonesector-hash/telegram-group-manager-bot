import { useEffect, useState } from 'react'
import EmptyState from '../components/ui/EmptyState'
import { useAppContext } from '../App'

function OrderCard({ order, onRenew, renewing }) {
  var created = order.created_at ? new Date(order.created_at).toLocaleString('fa-IR') : '—'
  var expires = order.expires_at ? new Date(order.expires_at).toLocaleDateString('fa-IR') : null
  var meta = order.metadata || {}
  var delivery = meta.delivery
  var renewable = /^\d+$/.test(String(order.item_key || '')) && meta.kind === 'vpn'
  function copyDelivery() {
    if (delivery && navigator.clipboard) navigator.clipboard.writeText(delivery)
  }
  return (
    <div className="glass" style={{padding:16,marginBottom:10}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
        <div style={{fontWeight:700,fontSize:15}}>{order.name || 'سفارش SectorLand'}</div>
        <span className="badge badge-green">{order.status === 'delivered' ? '🎁 تحویل شده' : order.status === 'active' ? '✅ فعال' : '✅ ثبت شده'}</span>
      </div>
      <div style={{fontSize:12,color:'var(--muted)',lineHeight:1.9}}>🧾 شناسه سفارش: {order.id}<br/>🪙 مبلغ: {Number(order.price || 0).toLocaleString()} سکه<br/>📅 زمان ثبت: {created}{expires && <><br/>⏳ اعتبار تا: {expires}</>}</div>
      {delivery && <div style={{marginTop:10,padding:10,borderRadius:10,background:'rgba(45,210,140,.08)',direction:'ltr',wordBreak:'break-all',fontSize:11}}>{delivery}<button className="btn btn-sm" onClick={copyDelivery} style={{marginTop:8,width:'100%'}}>📋 کپی جایزه</button></div>}
      {renewable && <button className="btn btn-primary btn-sm" disabled={renewing} onClick={function(){onRenew(order)}} style={{marginTop:10,width:'100%'}}>{renewing?'⏳ در حال تمدید':'🔄 تمدید اشتراک'}</button>}
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
  var [renewing,setRenewing] = useState(null)

  function renew(order) {
    if (renewing) return
    setRenewing(order.id)
    apiCall('renewOrder',tgUser.id,order.id).then(function(result){
      var data=result && result.data
      if (data && data.status==='success') {
        setOrders(function(rows){return rows.map(function(row){return row.id===order.id?data.order:row})})
        ctx.setDbUser(function(u){return {...u,coins:Number(data.coins)}})
        ctx.showToast(data.message,'success')
      } else ctx.showToast((data&&data.message)||(result&&result.error)||'تمدید انجام نشد.','error')
      setRenewing(null)
    })
  }

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
      {!loading && orders.map(function(order){return <OrderCard key={order.id} order={order} onRenew={renew} renewing={renewing===order.id} />})}
    </div>
  )
}
