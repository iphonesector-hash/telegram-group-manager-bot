import EmptyState from '../components/ui/EmptyState'
import { MOCK_ORDERS } from '../utils/mock'
import { useAppContext } from '../App'

function OrderCard({ order, navigate }) {
  var isActive = order.status === 'active'
  var pct = isActive ? Math.min(100, order.daysLeft * 2) : 0
  var barColor = order.daysLeft < 10
    ? 'linear-gradient(90deg,var(--red),#ff8040)'
    : 'linear-gradient(90deg,var(--accent),var(--accent2))'

  return (
    <div className="glass" style={{
      padding: '16px', marginBottom: 10,
      borderColor: isActive ? 'rgba(34,216,122,.3)' : 'var(--border)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <div style={{ fontWeight: 700, fontSize: 15 }}>{order.name}</div>
        <span className={'badge ' + (isActive ? 'badge-green' : 'badge-red')}>
          {isActive ? '✅ فعال' : '⏱️ منقضی'}
        </span>
      </div>
      <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: isActive ? 10 : 0 }}>
        📅 انقضا: {order.expires}
        {isActive && ' — ' + order.daysLeft + ' روز مانده'}
      </div>
      {isActive && (
        <div className="progress-bar" style={{ marginBottom: 0 }}>
          <div className="progress-fill" style={{ width: pct + '%', background: barColor }} />
        </div>
      )}
      {!isActive && (
        <button className="btn btn-ghost btn-sm" style={{ marginTop: 10 }}
          onClick={function() { navigate('shop') }}>
          🔄 تمدید کن
        </button>
      )}
    </div>
  )
}

export default function OrdersPage() {
  var ctx = useAppContext()
  var navigate = ctx.navigate
  var active = MOCK_ORDERS.filter(function(o) { return o.status === 'active' })
  var expired = MOCK_ORDERS.filter(function(o) { return o.status === 'expired' })

  return (
    <div className="page fade-up">
      <div className="sec-title">📦 سفارش‌های من</div>

      {MOCK_ORDERS.length === 0 && (
        <EmptyState
          icon="📦" title="سفارشی نداری هنوز"
          sub="برو فروشگاه و اولین VPN‌ات رو بخر"
          action="رفتن به فروشگاه"
          onAction={function() { navigate('shop') }}
        />
      )}

      {active.length > 0 && (
        <div>
          <div style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 10 }}>✅ فعال</div>
          {active.map(function(o) { return <OrderCard key={o.id} order={o} navigate={navigate} /> })}
        </div>
      )}

      {expired.length > 0 && (
        <div>
          <div style={{ fontSize: 13, color: 'var(--muted)', margin: '16px 0 10px' }}>🕛 منقضی‌شده</div>
          {expired.map(function(o) { return <OrderCard key={o.id} order={o} navigate={navigate} /> })}
        </div>
      )}
    </div>
  )
}
