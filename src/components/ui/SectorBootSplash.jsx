export default function SectorBootSplash(){
  return (
    <div style={{height:'100vh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:16,padding:24,background:'radial-gradient(circle at 50% 28%,rgba(112,68,255,.24),transparent 38%),#07091f',overflow:'hidden'}}>
      <div style={{width:'min(360px,88vw)',borderRadius:28,overflow:'hidden',border:'1px solid rgba(125,92,255,.32)',boxShadow:'0 28px 90px rgba(86,54,255,.26)',position:'relative'}}>
        <img src="/assets/sector/brand-hero.webp" alt="Sector" style={{display:'block',width:'100%',aspectRatio:'1.32',objectFit:'cover'}} />
        <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,transparent 55%,rgba(5,7,27,.82))'}} />
      </div>
      <div style={{fontWeight:950,fontSize:20,letterSpacing:.4}}>SECTOR</div>
      <div style={{color:'var(--muted)',fontSize:12}}>Play • Earn • Grow</div>
      <div className="spinner" />
      <div style={{color:'var(--muted)',fontSize:11}}>سکتور کوچولو داره بیدار می‌شه…</div>
    </div>
  )
}
