import { useState } from 'react'
import { WHEEL_PRIZES, WHEEL_COLORS } from '../utils/mock'
import { useAppContext } from '../App'

export default function WheelOfFortune() {
  var ctx = useAppContext()
  var [rotation, setRotation] = useState(0)
  var [spinning, setSpinning] = useState(false)
  var [lastPrize, setLastPrize] = useState(null)
  var slice = 360 / WHEEL_PRIZES.length
  var gradient = WHEEL_COLORS.map(function(color, i) {
    return color + ' ' + (i * slice) + 'deg ' + ((i + 1) * slice) + 'deg'
  }).join(',')

  function spin() {
    if (spinning || !ctx.tgUser) return
    setSpinning(true); setLastPrize(null)
    ctx.apiCall('spinWheel', ctx.tgUser.id).then(function(result) {
      var data = result && result.data
      if (!data || data.status !== 'success') {
        ctx.showToast((data && data.message) || 'گردونه فعلاً در دسترس نیست.', 'error')
        setSpinning(false)
        return
      }
      var target = Number(data.index || 0)
      var turns = 5 * 360
      var finalRotation = rotation + turns + (360 - (target * slice + slice / 2))
      setRotation(finalRotation)
      window.setTimeout(function() {
        setLastPrize(data.prize)
        setSpinning(false)
        if (data.coins != null) ctx.setDbUser(function(u) { return { ...u, coins:Number(data.coins) } })
        ctx.showToast('🎉 برندهٔ ' + data.prize.label + ' شدی!', 'success')
      }, 4200)
    })
  }

  return (
    <div className="glass" style={{padding:'24px 14px',textAlign:'center'}}>
      <div className="wheel-wrap">
        <div className="wheel-pointer">▼</div>
        <div aria-label="گردونه شانس" style={{width:240,height:240,borderRadius:'50%',background:'conic-gradient('+gradient+')',border:'7px solid rgba(255,255,255,.14)',boxShadow:'0 10px 35px rgba(0,0,0,.35)',transform:'rotate('+rotation+'deg)',transition:spinning?'transform 4s cubic-bezier(.12,.65,.12,1)':'none',position:'relative'}}>
          {WHEEL_PRIZES.map(function(prize, i) {
            return <span key={i} style={{position:'absolute',left:'50%',top:'50%',width:92,marginLeft:-46,marginTop:-9,transform:'rotate('+(i*slice+slice/2)+'deg) translateY(-88px)',fontSize:10,fontWeight:800,color:'#fff',textShadow:'0 1px 3px #000'}}>{prize.short}</span>
          })}
        </div>
      </div>
      <div style={{fontWeight:800,fontSize:18,marginTop:22}}>گردونهٔ شانس روزانه</div>
      <div style={{fontSize:12,color:'var(--muted)',lineHeight:1.8,margin:'6px 0 16px'}}>هر ۲۴ ساعت یک‌بار؛ جایزه شامل سکه، کانفیگ رایگان یا پروکسی تلگرام است.</div>
      {lastPrize && <div className="badge badge-gold" style={{marginBottom:12,fontSize:13}}>🎉 {lastPrize.label}</div>}
      <button className="btn btn-gold" onClick={spin} disabled={spinning} style={{width:'100%',padding:13}}>{spinning?'⏳ در حال چرخش...':'🎡 بچرخون'}</button>
    </div>
  )
}
