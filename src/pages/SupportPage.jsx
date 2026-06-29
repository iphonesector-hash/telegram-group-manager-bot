import { useState } from 'react'
import { MOCK_FAQ } from '../utils/mock'

export default function SupportPage() {
  var [openIdx, setOpenIdx] = useState(null)

  var channels = [
    { icon: '📢', label: 'کانال اصلی',   link: 'https://t.me/Vaslchannel' },
    { icon: '👥', label: 'گروه سکتور',   link: 'https://t.me/Vaslgroupp' },
    { icon: '🌐', label: 'سکتورلند',     link: 'https://t.me/sectorland' },
    { icon: '📩', label: 'تماس ادمین',   link: 'https://t.me/sector_ad' },
  ]

  return (
    <div className="page fade-up">
      <div className="sec-title">❓ پشتیبانی</div>

      {/* Contact card */}
      <div className="glass" style={{
        padding: '24px', textAlign: 'center', marginBottom: 16,
        background: 'linear-gradient(135deg,rgba(79,123,255,.12),rgba(162,89,255,.06))'
      }}>
        <div style={{ fontSize: 44, marginBottom: 10 }}>💬</div>
        <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>پشتیبانی آنلاین</div>
        <div style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 16, lineHeight: 1.6 }}>
          پاسخ‌گو ۲۴/۷ — معمولاً ظرف ۳۰ دقیقه پاسخ داده می‌شه
        </div>
        <a href="https://t.me/sector_ad" target="_blank" rel="noreferrer"
          className="btn btn-primary"
          style={{ display: 'inline-flex', textDecoration: 'none', padding: '12px 28px', borderRadius: 12, fontSize: 14 }}>
          💬 ارتباط با پشتیبانی
        </a>
      </div>

      {/* Channels */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 24 }}>
        {channels.map(function(c, i) {
          return (
            <a key={i} href={c.link} target="_blank" rel="noreferrer"
              className="glass btn"
              style={{
                textDecoration: 'none', flexDirection: 'column',
                gap: 6, padding: '14px 8px',
                border: '1px solid var(--border)', color: 'var(--text)'
              }}>
              <span style={{ fontSize: 24 }}>{c.icon}</span>
              <span style={{ fontSize: 12, fontWeight: 600 }}>{c.label}</span>
            </a>
          )
        })}
      </div>

      {/* FAQ */}
      <div className="sec-title">📚 سؤالات متداول</div>
      {MOCK_FAQ.map(function(f, i) {
        var isOpen = openIdx === i
        return (
          <div key={i} className="glass faq-item" style={{ marginBottom: 8 }}>
            <button onClick={function() { setOpenIdx(isOpen ? null : i) }}
              style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                width: '100%', padding: '14px 16px',
                background: 'transparent', border: 'none',
                color: 'var(--text)', cursor: 'pointer',
                fontFamily: 'Vazirmatn, sans-serif', textAlign: 'right'
              }}>
              <span style={{ fontSize: 13, fontWeight: 600, flex: 1 }}>{f.q}</span>
              <span style={{
                color: 'var(--muted)', fontSize: 18, marginRight: 10,
                transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
                transition: 'transform .2s', display: 'inline-block'
              }}>↓</span>
            </button>
            {isOpen && (
              <div className="faq-answer">{f.a}</div>
            )}
          </div>
        )
      })}
      <div style={{ height: 16 }} />
    </div>
  )
}
