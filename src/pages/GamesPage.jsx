import { useEffect, useState } from 'react'
import { useAppContext } from '../App'

export default function GamesPage() {
  var ctx = useAppContext()
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var showToast = ctx.showToast
  var apiCall = ctx.apiCall
  var tgUser = ctx.tgUser

  var [tab, setTab] = useState('games')
  var [games, setGames] = useState([])
  var [leaderboard, setLeaderboard] = useState([])
  var [loading, setLoading] = useState(false)
  var [claiming, setClaiming] = useState(false)

  useEffect(function() {
    if (!tgUser) return
    setLoading(true)
    Promise.all([
      apiCall('getGames'),
      apiCall('getLeaderboard'),
    ]).then(function(results) {
      setGames(Array.isArray(results[0] && results[0].data) ? results[0].data : [])
      setLeaderboard(Array.isArray(results[1] && results[1].data) ? results[1].data : [])
      setLoading(false)
    })
  }, [tgUser, apiCall])

  function claimDaily() {
    if (!tgUser || claiming) return
    setClaiming(true)
    apiCall('dailyClaim', tgUser.id).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'success') {
        setDbUser(function(u) { return { ...u, coins: Number(data.coins || u.coins || 0) } })
        showToast('🎁 +' + data.reward + ' سکه دریافت کردی!', 'success')
      } else {
        showToast((data && data.message) || 'فعلاً جایزه روزانه در دسترس نیست.', 'error')
      }
      setClaiming(false)
    })
  }

  var tabs = [
    { key: 'games', label: '🎮 بازی‌ها' },
    { key: 'daily', label: '🎁 جایزه روزانه' },
    { key: 'leaderboard', label: '🏆 برترین‌ها' },
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

      {loading && <div className="glass" style={{padding:20,textAlign:'center',color:'var(--muted)'}}>در حال همگام‌سازی با ربات...</div>}

      {!loading && tab === 'games' && (
        <div>
          {games.length === 0 && <div className="glass" style={{padding:20,textAlign:'center',color:'var(--muted)'}}>فعلاً بازی فعالی ثبت نشده.</div>}
          {games.map(function(g) {
            return (
              <div key={g.id} className="glass" style={{padding:'15px 16px',marginBottom:10,display:'flex',alignItems:'center',gap:12}}>
                <div style={{width:42,height:42,borderRadius:13,background:'rgba(79,123,255,.12)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:21}}>
                  {g.id === 'quiz' ? '🧠' : g.id === 'logic' ? '🧩' : g.id === 'flag' ? '🚩' : '🎮'}
                </div>
                <div style={{flex:1}}>
                  <div style={{fontWeight:700,fontSize:14}}>{g.name}</div>
                  <div style={{fontSize:11,color:'var(--muted)',marginTop:3}}>{g.active ? 'همگام با حساب SectorBot' : 'به‌زودی'}</div>
                </div>
                <span className={g.active ? 'badge badge-green' : 'badge'}>{g.active ? 'فعال' : 'غیرفعال'}</span>
              </div>
            )
          })}
          <div className="glass" style={{padding:14,marginTop:12,color:'var(--muted)',fontSize:12,lineHeight:1.8}}>
            امتیاز، XP و سکه بازی‌ها از همان حساب ربات خوانده می‌شود. نسخه بعدی کوییزهای چندگزینه‌ای را مستقیم داخل همین Mini App اجرا می‌کند.
          </div>
        </div>
      )}

      {!loading && tab === 'daily' && (
        <div style={{textAlign:'center',paddingTop:18}}>
          <div className="glass" style={{padding:'28px 18px',maxWidth:360,margin:'0 auto'}}>
            <div style={{fontSize:54,marginBottom:10}}>🎁</div>
            <div style={{fontWeight:800,fontSize:18,marginBottom:8}}>جایزه روزانه SectorLand</div>
            <div style={{color:'var(--muted)',fontSize:13,lineHeight:1.8,marginBottom:20}}>این جایزه دقیقاً روی موجودی واقعی ربات ثبت می‌شود و هر ۲۴ ساعت یک بار قابل دریافت است.</div>
            <button className="btn btn-gold" onClick={claimDaily} disabled={claiming} style={{padding:'13px 28px',borderRadius:14}}>
              {claiming ? '⏳ در حال ثبت...' : '🎁 دریافت جایزه'}
            </button>
            <div style={{marginTop:16,fontSize:12,color:'var(--muted)'}}>موجودی فعلی: <span style={{color:'var(--gold)',fontWeight:700}}>{Number(dbUser.coins || 0).toLocaleString()} 🪙</span></div>
          </div>
        </div>
      )}

      {!loading && tab === 'leaderboard' && (
        <div>
          <div className="glass" style={{padding:'12px 16px',marginBottom:12,background:'linear-gradient(135deg,rgba(79,123,255,.1),rgba(162,89,255,.06))'}}>
            <div style={{fontSize:12,color:'var(--muted)',marginBottom:4}}>رتبه من</div>
            <div style={{fontWeight:800,fontSize:20}}>#{Number(dbUser.rank || 0).toLocaleString('fa-IR')}</div>
          </div>
          {leaderboard.map(function(u, i) {
            var badge = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : u.rank
            return (
              <div key={i} className="glass" style={{padding:'12px 14px',marginBottom:8,display:'flex',alignItems:'center',gap:12}}>
                <div style={{width:34,height:34,borderRadius:'50%',background:'var(--card)',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:800}}>{badge}</div>
                <div style={{flex:1}}><div style={{fontWeight:700,fontSize:13}}>{u.name}</div><div style={{fontSize:11,color:'var(--muted)'}}>سطح {u.level}</div></div>
                <div style={{fontWeight:800,color:'var(--gold)',fontSize:14}}>{Number(u.coins || 0).toLocaleString()} 🪙</div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
