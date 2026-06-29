import { useState, useEffect, useRef } from 'react'
import { MOCK_MISSIONS, MOCK_LEADERBOARD, WHEEL_PRIZES, WHEEL_COLORS } from '../utils/mock'
import { useAppContext } from '../App'

function drawWheel(canvas) {
  if (!canvas) return
  var ctx = canvas.getContext('2d')
  var n = WHEEL_PRIZES.length
  var arc = (2 * Math.PI) / n
  var r = canvas.width / 2
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  WHEEL_PRIZES.forEach(function(p, i) {
    var start = arc * i
    ctx.beginPath()
    ctx.moveTo(r, r)
    ctx.arc(r, r, r - 3, start, start + arc)
    ctx.fillStyle = WHEEL_COLORS[i]
    ctx.fill()
    ctx.strokeStyle = 'rgba(0,0,0,.25)'
    ctx.lineWidth = 1.5
    ctx.stroke()
    ctx.save()
    ctx.translate(r, r)
    ctx.rotate(start + arc / 2)
    ctx.textAlign = 'right'
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 10px Vazirmatn'
    ctx.fillText(p.label, r - 10, 4)
    ctx.restore()
  })
  ctx.beginPath()
  ctx.arc(r, r, 16, 0, 2 * Math.PI)
  ctx.fillStyle = '#080b14'
  ctx.fill()
  ctx.strokeStyle = 'rgba(255,255,255,.15)'
  ctx.lineWidth = 2
  ctx.stroke()
}

export default function GamesPage() {
  var ctx = useAppContext()
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var showToast = ctx.showToast
  var [tab, setTab] = useState('missions')
  var [spinning, setSpinning] = useState(false)
  var [rotation, setRotation] = useState(0)
  var canvasRef = useRef(null)

  useEffect(function() {
    drawWheel(canvasRef.current)
  }, [])

  function spinWheel() {
    if (spinning) return
    setSpinning(true)
    var extra = 360 * (5 + Math.floor(Math.random() * 4))
    var prizeIdx = Math.floor(Math.random() * WHEEL_PRIZES.length)
    var prizeAngle = prizeIdx * (360 / WHEEL_PRIZES.length)
    var finalRot = rotation + extra + (360 - prizeAngle)
    setRotation(finalRot)
    setTimeout(function() {
      setSpinning(false)
      var prize = WHEEL_PRIZES[prizeIdx]
      setDbUser(function(u) { return { ...u, coins: u.coins + prize.coins } })
      showToast('🎉 ' + prize.label + ' برنده شدی!', 'success')
    }, 3600)
  }

  var tabs = [
    { key: 'missions',     label: '🎯 مأموریت‌ها' },
    { key: 'wheel',        label: '🎰 گردونه' },
    { key: 'leaderboard',  label: '🏆 برترین‌ها' },
  ]

  return (
    <div className="page fade-up">
      <div className="sec-title">🎮 بازی و جوایز</div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 18, flexWrap: 'wrap' }}>
        {tabs.map(function(t) {
          return (
            <button key={t.key} onClick={function() { setTab(t.key) }} className="btn btn-sm"
              style={{
                background: tab === t.key ? 'linear-gradient(135deg,var(--accent),var(--accent2))' : 'var(--card)',
                color: tab === t.key ? '#fff' : 'var(--muted)',
                border: tab === t.key ? 'none' : '1px solid var(--border)', fontSize: 11
              }}>
              {t.label}
            </button>
          )
        })}
      </div>

      {/* Missions */}
      {tab === 'missions' && (
        <div>
          {MOCK_MISSIONS.map(function(m) {
            var pct = Math.min(100, Math.round((m.progress / m.total) * 100))
            return (
              <div key={m.id} className="glass" style={{
                padding: '14px 16px', marginBottom: 10,
                borderColor: m.done ? 'rgba(34,216,122,.3)' : 'var(--border)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 14 }}>{m.done ? '✅' : '🎯'} {m.title}</div>
                    <div style={{ color: 'var(--muted)', fontSize: 12, marginTop: 2 }}>{m.desc}</div>
                  </div>
                  <span className="badge badge-gold">+{m.reward} 🪙</span>
                </div>
                {!m.done && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>
                      <span>پیشرفت</span>
                      <span>{m.progress.toLocaleString()} / {m.total.toLocaleString()}</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: pct + '%' }} />
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Wheel */}
      {tab === 'wheel' && (
        <div style={{ textAlign: 'center', paddingTop: 10 }}>
          <div style={{ position: 'relative', width: 240, height: 240, margin: '0 auto 20px' }}>
            <div style={{ position: 'absolute', top: -14, left: '50%', transform: 'translateX(-50%)', fontSize: 28, zIndex: 10 }}>▼</div>
            <canvas
              ref={canvasRef}
              width={240}
              height={240}
              style={{
                borderRadius: '50%',
                border: '3px solid var(--border)',
                transform: 'rotate(' + rotation + 'deg)',
                transition: spinning ? 'transform 3.6s cubic-bezier(.17,.67,.12,1)' : 'none'
              }}
            />
          </div>
          <div style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 20 }}>
            هر ۲۴ ساعت یه بار می‌تونی بچرخونی!
          </div>
          <button className="btn btn-gold pulse-glow" style={{ padding: '14px 44px', fontSize: 15, borderRadius: 16 }}
            onClick={spinWheel} disabled={spinning}>
            {spinning ? '⏳ در حال چرخش...' : '🎰 بچرخون!'}
          </button>
          <div style={{ marginTop: 16, fontSize: 12, color: 'var(--muted)' }}>
            موجودی فعلی: <span style={{ color: 'var(--gold)', fontWeight: 700 }}>{dbUser.coins.toLocaleString()} 🪙</span>
          </div>
        </div>
      )}

      {/* Leaderboard */}
      {tab === 'leaderboard' && (
        <div>
          <div className="glass" style={{
            padding: '12px 16px', marginBottom: 12,
            background: 'linear-gradient(135deg,rgba(79,123,255,.1),rgba(162,89,255,.06))'
          }}>
            <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>رتبه من</div>
            <div style={{ fontWeight: 800, fontSize: 20 }}>#{dbUser.rank} از ۱۰۰۰+ کاربر</div>
          </div>
          {MOCK_LEADERBOARD.map(function(u, i) {
            var isTop3 = i < 3
            return (
              <div key={i} className="glass" style={{
                padding: '12px 14px', marginBottom: 8,
                borderColor: i === 0 ? 'rgba(245,200,66,.4)' : i === 1 ? 'rgba(200,200,200,.3)' : i === 2 ? 'rgba(205,127,50,.3)' : 'var(--border)',
                background: i === 0 ? 'rgba(245,200,66,.05)' : 'transparent'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 34, height: 34, borderRadius: '50%', flexShrink: 0,
                    background: isTop3 ? (i === 0 ? 'rgba(245,200,66,.2)' : 'rgba(200,200,200,.15)') : 'var(--card)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 800, fontSize: 14
                  }}>
                    {u.badge || u.rank}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: 13 }}>{u.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--muted)' }}>سطح {u.level}</div>
                  </div>
                  <div style={{ fontWeight: 800, color: 'var(--gold)', fontSize: 14 }}>
                    {u.coins.toLocaleString()} 🪙
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
