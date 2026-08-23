import { useEffect, useState } from 'react'
import { useAppContext } from '../App'
import WheelOfFortune from '../components/WheelOfFortune'

const ARCADE_GAMES = [
  {id:'racer',name:'Neon Racer',icon:'🏎️',desc:'مسابقه سریع در بزرگراه نئونی',type:'اکشن',featured:true,url:'https://sectorland-neon-arcade.vercel.app/games/neon-racer/'},
  {id:'galaxy',name:'Galaxy Defender',icon:'🚀',desc:'نبرد فضایی، باس و موج‌های سخت',type:'شوتر',featured:true,url:'https://sectorland-neon-arcade.vercel.app/games/galaxy-defender/'},
  {id:'snake3d',name:'Snake 3D',icon:'🐍',desc:'مار سه‌بعدی سکتور با مراحل مختلف',type:'سه‌بعدی',featured:true,url:'https://love-hub-snake-3-d.vercel.app'},
  {id:'2048',name:'2048',icon:'🔢',desc:'ترکیب اعداد و رکوردشکنی',type:'فکری',url:'https://lovehub-games.vercel.app/games/2048/'},
  {id:'tetris',name:'تتریس لمسی',icon:'🧱',desc:'چیدن بلوک‌ها با کنترل موبایل',type:'آرکید',url:'https://lovehub-games.vercel.app/games/tetris-touch/'},
  {id:'memory',name:'بازی حافظه',icon:'🧠',desc:'پیداکردن کارت‌های مشابه',type:'فکری',url:'https://lovehub-games.vercel.app/games/memory/src/'},
  {id:'mines',name:'مین‌یاب',icon:'💣',desc:'معمای کلاسیک و منطقی مین‌ها',type:'فکری',url:'https://lovehub-games.vercel.app/games/minesweeper/'},
]

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
  var [quiz, setQuiz] = useState(null)
  var [quizLoading, setQuizLoading] = useState(false)
  var [answering, setAnswering] = useState(false)
  var [result, setResult] = useState(null)
  var [gameFilter, setGameFilter] = useState('همه')
  var [lastGame, setLastGame] = useState(function(){
    try { return window.localStorage.getItem('sectorland_last_game') || '' } catch (_) { return '' }
  })

  useEffect(function() {
    if (!tgUser) return
    setLoading(true)
    Promise.all([apiCall('getGames'), apiCall('getLeaderboard')]).then(function(results) {
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
      } else showToast((data && data.message) || 'فعلاً جایزه روزانه در دسترس نیست.', 'error')
      setClaiming(false)
    })
  }

  function startQuiz(kind) {
    setQuizLoading(true); setResult(null); setQuiz(null)
    apiCall('getQuiz', kind).then(function(r) {
      setQuiz(r && r.data ? r.data : null)
      if (!r || !r.data) showToast('سؤال جدید دریافت نشد.', 'error')
      setQuizLoading(false)
    })
  }

  function answer(choice) {
    if (!quiz || !tgUser || answering || result) return
    setAnswering(true)
    apiCall('answerQuiz', tgUser.id, quiz.id, choice).then(function(r) {
      var data = r && r.data
      if (!data) {
        showToast('ثبت پاسخ انجام نشد.', 'error')
      } else if (data.status === 'already_answered') {
        showToast(data.message || 'قبلاً پاسخ دادی.', 'error')
        setResult(data)
      } else {
        setResult(data)
        if (data.correct && data.user) {
          setDbUser(function(u) { return { ...u, coins: data.user.coins, xp: data.user.xp, level: data.user.level } })
          showToast('✅ درست! +' + data.reward.coins + ' سکه و +' + data.reward.xp + ' XP', 'success')
        } else showToast('❌ جواب درست نبود.', 'error')
      }
      setAnswering(false)
    })
  }

  function openArcade(game) {
    setLastGame(game.id)
    try { window.localStorage.setItem('sectorland_last_game', game.id) } catch (_) {}
    try { ctx.tg && ctx.tg.HapticFeedback && ctx.tg.HapticFeedback.impactOccurred('medium') } catch (_) {}
    try {
      if (ctx.tg && ctx.tg.openLink) ctx.tg.openLink(game.url)
      else window.location.assign(game.url)
    } catch (_) { window.location.assign(game.url) }
  }

  var tabs = [
    { key: 'games', label: '🎮 بازی‌ها' },
    { key: 'daily', label: '🎁 جایزه روزانه' },
    { key: 'wheel', label: '🎡 گردونه شانس' },
    { key: 'leaderboard', label: '🏆 برترین‌ها' },
  ]

  return (
    <div className="page fade-up">
      <div className="sec-title">🎮 بازی و جوایز</div>
      <div style={{ display:'flex', gap:8, marginBottom:18, flexWrap:'wrap' }}>
        {tabs.map(function(t){return <button key={t.key} onClick={function(){setTab(t.key)}} className="btn btn-sm" style={{background:tab===t.key?'linear-gradient(135deg,var(--accent),var(--accent2))':'var(--card)',color:tab===t.key?'#fff':'var(--muted)',border:tab===t.key?'none':'1px solid var(--border)',fontSize:11}}>{t.label}</button>})}
      </div>

      {loading && <div className="glass" style={{padding:20,textAlign:'center',color:'var(--muted)'}}>در حال همگام‌سازی با ربات...</div>}

      {!loading && tab === 'games' && (
        <div>
          <div className="glass" style={{padding:18,marginBottom:14,background:'radial-gradient(circle at 15% 10%,rgba(0,238,255,.2),transparent 42%),linear-gradient(135deg,rgba(91,43,255,.22),rgba(255,43,175,.1))',overflow:'hidden'}}>
            <div style={{fontSize:11,color:'#6ff7ff',fontWeight:900}}>SECTORLAND ARCADE</div>
            <div style={{fontWeight:900,fontSize:20,marginTop:5}}>مرکز بازی‌های حرفه‌ای</div>
            <div style={{fontSize:11,color:'var(--muted)',lineHeight:1.8,marginTop:5}}>بازی‌های لمسی، تمام‌صفحه و سبک؛ بدون نصب و مناسب تلگرام</div>
          </div>
          {lastGame && ARCADE_GAMES.some(function(g){return g.id===lastGame}) && <button className="btn" onClick={function(){openArcade(ARCADE_GAMES.find(function(g){return g.id===lastGame}))}} style={{width:'100%',marginBottom:12,background:'linear-gradient(135deg,rgba(0,210,255,.15),rgba(143,66,255,.15))',border:'1px solid rgba(80,220,255,.25)',color:'inherit'}}>▶️ ادامه آخرین بازی</button>}
          <div style={{display:'flex',gap:7,overflowX:'auto',paddingBottom:10}}>{['همه','اکشن','شوتر','سه‌بعدی','فکری','آرکید'].map(function(f){return <button key={f} className="btn btn-sm" onClick={function(){setGameFilter(f)}} style={{flex:'0 0 auto',background:gameFilter===f?'linear-gradient(135deg,#04bfe8,#714cff)':'var(--card)',color:gameFilter===f?'#fff':'var(--muted)',border:'1px solid var(--border)'}}>{f}</button>})}</div>
          <div style={{fontWeight:800,fontSize:14,margin:'2px 0 10px'}}>🕹 بازی‌های کامل</div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:20}}>
            {ARCADE_GAMES.filter(function(game){return gameFilter==='همه'||game.type===gameFilter}).map(function(game){return <button key={game.id} onClick={function(){openArcade(game)}} className="glass" style={{padding:14,border:game.featured?'1px solid rgba(69,227,255,.35)':'1px solid var(--border)',background:game.featured?'linear-gradient(145deg,rgba(25,201,255,.1),rgba(119,57,255,.1))':'var(--card)',color:'inherit',textAlign:'right',cursor:'pointer',minHeight:145,position:'relative'}}>{game.featured&&<span style={{position:'absolute',top:9,left:9,fontSize:9,color:'#06131c',fontWeight:900,padding:'4px 7px',borderRadius:10,background:'#66f2ff'}}>ویژه</span>}<div style={{fontSize:34}}>{game.icon}</div><div style={{fontWeight:800,fontSize:14,marginTop:7}}>{game.name}</div><div style={{fontSize:10,color:'var(--muted)',lineHeight:1.6,marginTop:3}}>{game.desc}</div><div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:9}}><span className="badge badge-blue">بازی کن</span><span style={{fontSize:9,color:'var(--muted)'}}>{game.type}</span></div></button>})}
          </div>
          <div style={{fontWeight:800,fontSize:14,margin:'2px 0 10px'}}>🧩 مسابقه‌های سکه‌ای ربات</div>
          {games.map(function(g){
            return <button key={g.id} onClick={function(){startQuiz(g.id)}} className="glass" style={{width:'100%',padding:'15px 16px',marginBottom:10,display:'flex',alignItems:'center',gap:12,border:'1px solid var(--border)',color:'inherit',textAlign:'right',cursor:'pointer'}}>
              <div style={{width:42,height:42,borderRadius:13,background:'rgba(79,123,255,.12)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:21}}>{g.id==='intel'?'🧠':g.id==='logic'?'🧩':'🚩'}</div>
              <div style={{flex:1}}><div style={{fontWeight:700,fontSize:14}}>{g.name}</div><div style={{fontSize:11,color:'var(--muted)',marginTop:3}}>پاسخ درست = سکه + XP واقعی</div></div>
              <span className="badge badge-green">شروع</span>
            </button>
          })}

          {quizLoading && <div className="glass" style={{padding:18,textAlign:'center'}}>⏳ در حال آوردن سؤال...</div>}
          {quiz && !quizLoading && <div className="glass" style={{padding:18,marginTop:14}}>
            <div style={{fontSize:12,color:'var(--muted)',marginBottom:8}}>جایزه: 🪙 {quiz.reward.coins} + ⭐ {quiz.reward.xp} XP</div>
            <div style={{fontWeight:800,fontSize:16,lineHeight:1.9,marginBottom:14}}>{quiz.question}</div>
            <div style={{display:'grid',gap:8}}>
              {quiz.options.map(function(opt,i){
                var chosen = result && result.correct_index === i
                return <button key={i} disabled={answering || !!result} onClick={function(){answer(i)}} className="btn" style={{padding:'12px 14px',justifyContent:'flex-start',background:chosen?'rgba(34,216,122,.15)':'var(--card)',border:'1px solid var(--border)',color:'inherit'}}>{String.fromCharCode(65+i)}. {opt}</button>
              })}
            </div>
            {result && <div style={{marginTop:14,padding:12,borderRadius:12,background:result.correct?'rgba(34,216,122,.1)':'rgba(255,79,106,.1)',lineHeight:1.8,fontSize:13}}>{result.correct?'✅ پاسخ درست بود!':'❌ پاسخ اشتباه بود.'}<br/>{result.explanation || result.message || ''}</div>}
            {result && <button onClick={function(){startQuiz(quiz.kind)}} className="btn btn-primary" style={{marginTop:12,width:'100%'}}>🔄 سؤال بعدی</button>}
          </div>}
        </div>
      )}

      {!loading && tab === 'daily' && <div style={{textAlign:'center',paddingTop:18}}><div className="glass" style={{padding:'28px 18px',maxWidth:360,margin:'0 auto'}}><div style={{fontSize:54,marginBottom:10}}>🎁</div><div style={{fontWeight:800,fontSize:18,marginBottom:8}}>جایزه روزانه SectorLand</div><div style={{color:'var(--muted)',fontSize:13,lineHeight:1.8,marginBottom:20}}>این جایزه مستقیم روی حساب واقعی ربات ثبت می‌شود.</div><button className="btn btn-gold" onClick={claimDaily} disabled={claiming} style={{padding:'13px 28px',borderRadius:14}}>{claiming?'⏳ در حال ثبت...':'🎁 دریافت جایزه'}</button><div style={{marginTop:16,fontSize:12,color:'var(--muted)'}}>موجودی فعلی: <span style={{color:'var(--gold)',fontWeight:700}}>{Number(dbUser.coins||0).toLocaleString()} 🪙</span></div></div></div>}

      {!loading && tab === 'wheel' && <WheelOfFortune />}

      {!loading && tab === 'leaderboard' && <div><div className="glass" style={{padding:'12px 16px',marginBottom:12}}><div style={{fontSize:12,color:'var(--muted)'}}>رتبه من</div><div style={{fontWeight:800,fontSize:20}}>#{Number(dbUser.rank||0).toLocaleString('fa-IR')}</div></div>{leaderboard.map(function(u,i){var badge=i===0?'🥇':i===1?'🥈':i===2?'🥉':u.rank;return <div key={i} className="glass" style={{padding:'12px 14px',marginBottom:8,display:'flex',alignItems:'center',gap:12}}><div style={{width:34,height:34,borderRadius:'50%',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:800}}>{badge}</div><div style={{flex:1}}><div style={{fontWeight:700,fontSize:13}}>{u.name}</div><div style={{fontSize:11,color:'var(--muted)'}}>سطح {u.level}</div></div><div style={{fontWeight:800,color:'var(--gold)',fontSize:14}}>{Number(u.coins||0).toLocaleString()} 🪙</div></div>})}</div>}
    </div>
  )
}
