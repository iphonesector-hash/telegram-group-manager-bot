import { useAppContext } from '../App'

export default function ReferralPage() {
  var ctx = useAppContext()
  var tgUser = ctx.tgUser
  var dbUser = ctx.dbUser
  var showToast = ctx.showToast
  var refLink = 'https://t.me/SectorLandBot?start=ref_' + (tgUser ? tgUser.id : '00000')

  function copyLink() {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(refLink)
        .then(function() { showToast('🔗 لینک کپی شد!', 'success') })
        .catch(function() { showToast('لطفاً دستی کپی کن', 'info') })
    } else {
      showToast('لطفاً دستی کپی کن', 'info')
    }
  }

  var stats = [
    { icon: '👥', label: 'دعوت‌شده‌ها',   val: dbUser.referrals + ' نفر' },
    { icon: '💰', label: 'سکه کسب شده',   val: '۱,۶۰۰ 🪙' },
    { icon: '⏳', label: 'در انتظار',      val: '۲ نفر' },
  ]

  var steps = [
    'لینک اختصاصیت رو کپی کن',
    'برای دوستات بفرست',
    'وقتی ثبت‌نام کنن، هر دو سکه می‌گیرید!',
  ]

  return (
    <div className="page fade-up">
      <div className="sec-title">👥 سیستم معرفی</div>

      {/* Hero */}
      <div className="glass" style={{
        padding: '24px', textAlign: 'center', marginBottom: 16,
        background: 'linear-gradient(135deg,rgba(34,216,122,.12),rgba(34,216,122,.03))'
      }}>
        <div style={{ fontSize: 48, marginBottom: 8 }}>🤝</div>
        <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 8 }}>دوستات رو دعوت کن</div>
        <div style={{ color: 'var(--muted)', fontSize: 13, lineHeight: 1.7 }}>
          به ازای هر نفری که از لینک تو ثبت‌نام کنه
          <br />
          <strong style={{ color: 'var(--green)' }}>۲۰۰ سکه</strong> می‌گیری!
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 16 }}>
        {stats.map(function(s, i) {
          return (
            <div key={i} className="stat-pill">
              <div style={{ fontSize: 20, marginBottom: 4 }}>{s.icon}</div>
              <div style={{ fontWeight: 800, fontSize: 15, color: 'var(--green)' }}>{s.val}</div>
              <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>{s.label}</div>
            </div>
          )
        })}
      </div>

      {/* Link */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 8 }}>لینک اختصاصی تو:</div>
        <div className="ref-box">{refLink}</div>
        <button className="btn btn-primary" style={{ marginTop: 10 }} onClick={copyLink}>
          📋 کپی لینک
        </button>
      </div>

      {/* Steps */}
      <div className="glass" style={{ padding: '16px' }}>
        <div style={{ fontWeight: 700, marginBottom: 14 }}>چطور کار می‌کنه؟</div>
        {steps.map(function(s, i) {
          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 0',
              borderBottom: i < steps.length - 1 ? '1px solid var(--border)' : 'none'
            }}>
              <div style={{
                width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                background: 'linear-gradient(135deg,var(--accent),var(--accent2))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 800, fontSize: 13, color: '#fff'
              }}>
                {i + 1}
              </div>
              <span style={{ fontSize: 13 }}>{s}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
