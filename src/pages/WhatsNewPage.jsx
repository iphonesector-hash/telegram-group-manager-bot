import release from '../../release/current.json'
import { useAppContext } from '../App'

export default function WhatsNewPage() {
  var ctx = useAppContext()
  var tg = ctx.tg
  var features = Array.isArray(release.features) ? release.features : []
  var usage = Array.isArray(release.usage) ? release.usage : []

  function openChannel() {
    var url = 'https://t.me/sectorlandS'
    try {
      if (tg && tg.openTelegramLink) tg.openTelegramLink(url)
      else window.open(url, '_blank', 'noopener,noreferrer')
    } catch (_) { window.location.href = url }
  }

  return (
    <div className="page fade-up">
      <div className="glass" style={{overflow:'hidden',padding:0,marginBottom:14,border:'1px solid rgba(112,85,255,.35)',background:'#090c27'}}>
        <img src={release.image || '/assets/sector/brand-hero.webp'} alt="آخرین آپدیت سکتور کوچولو" style={{display:'block',width:'100%',aspectRatio:'1.32',objectFit:'cover'}} />
        <div style={{padding:'15px 16px'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,marginBottom:7}}>
            <b style={{fontSize:17}}>{release.title || 'آپدیت سکتور کوچولو'}</b>
            <span className="badge badge-purple">v{release.version || '1.0'}</span>
          </div>
          <div style={{fontSize:12,color:'var(--muted)',lineHeight:1.9}}>{release.summary}</div>
        </div>
      </div>

      <div className="sec-title">✨ امکانات جدید</div>
      <div className="glass" style={{padding:'8px 14px',marginBottom:18}}>
        {features.map(function(item, i){return <div key={i} style={{display:'flex',gap:10,padding:'11px 0',borderBottom:i<features.length-1?'1px solid var(--border)':'none',lineHeight:1.8,fontSize:13}}><span>✦</span><span>{item}</span></div>})}
      </div>

      <div className="sec-title">🧭 نحوه استفاده</div>
      <div className="glass" style={{padding:'8px 14px',marginBottom:18}}>
        {usage.map(function(item, i){return <div key={i} style={{display:'flex',gap:11,padding:'11px 0',borderBottom:i<usage.length-1?'1px solid var(--border)':'none',lineHeight:1.8,fontSize:13}}><span style={{width:25,height:25,borderRadius:8,background:'rgba(79,123,255,.14)',color:'var(--accent)',display:'inline-flex',alignItems:'center',justifyContent:'center',flex:'0 0 auto',fontWeight:800}}>{i+1}</span><span>{item}</span></div>})}
      </div>

      <button className="btn btn-primary" onClick={openChannel} style={{marginBottom:10}}>📣 کانال رسمی سکتور کوچولو</button>
      <div className="glass" style={{padding:'13px 15px',fontSize:12,color:'var(--muted)',lineHeight:1.8,textAlign:'center'}}>هر آپدیت جدید هم اینجا نمایش داده می‌شود و هم همراه تصویر و آموزش در @sectorlandS منتشر می‌شود.</div>
      <div style={{height:16}} />
    </div>
  )
}
