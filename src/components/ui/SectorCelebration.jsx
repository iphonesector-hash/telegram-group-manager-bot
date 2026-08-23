import { useEffect } from 'react'

export default function SectorCelebration({ open, title, text, onClose }) {
  useEffect(function () {
    if (!open) return
    var timer = window.setTimeout(function () { if (onClose) onClose() }, 2200)
    return function () { window.clearTimeout(timer) }
  }, [open, onClose])

  if (!open) return null
  return (
    <div onClick={onClose} style={{position:'fixed',inset:0,zIndex:80,display:'flex',alignItems:'center',justifyContent:'center',padding:24,background:'rgba(2,5,18,.76)',backdropFilter:'blur(12px)'}}>
      <div className="glass" onClick={function(e){e.stopPropagation()}} style={{width:'min(360px,92vw)',overflow:'hidden',textAlign:'center',border:'1px solid rgba(255,195,62,.38)',boxShadow:'0 24px 80px rgba(74,54,255,.35)',background:'linear-gradient(160deg,rgba(20,25,75,.98),rgba(9,10,35,.98))'}}>
        <div style={{position:'relative',height:205,overflow:'hidden'}}>
          <img src="/assets/sector/mascot-emotions.webp" alt="Sector celebration" style={{width:'145%',maxWidth:'none',position:'absolute',left:'50%',top:'50%',transform:'translate(-50%,-48%) scale(1.04)',filter:'drop-shadow(0 12px 34px rgba(123,92,255,.55))'}} />
          <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,transparent 45%,rgba(9,10,35,.96) 100%)'}} />
          <div style={{position:'absolute',left:0,right:0,bottom:8,fontSize:38}}>✨ 🪙 ✨</div>
        </div>
        <div style={{padding:'4px 18px 20px'}}>
          <div style={{fontWeight:950,fontSize:20,color:'var(--gold)'}}>{title || 'جایزه گرفتی!'}</div>
          <div style={{fontSize:12,lineHeight:1.9,color:'var(--muted)',marginTop:7}}>{text || 'پاداش با موفقیت روی حساب SectorLand ثبت شد.'}</div>
          <button className="btn btn-gold" onClick={onClose} style={{width:'100%',marginTop:14}}>عالیه! 🚀</button>
        </div>
      </div>
    </div>
  )
}
