export default function PageHeader({ title, onBack }) {
  return (
    <header style={{display:'flex',alignItems:'center',gap:10,padding:'calc(10px + env(safe-area-inset-top)) 14px 10px',borderBottom:'1px solid var(--border)',background:'rgba(8,11,20,.92)',backdropFilter:'blur(16px)',position:'relative',zIndex:20}}>
      <button type="button" aria-label="بازگشت" onClick={onBack} className="btn" style={{width:42,height:42,minWidth:42,padding:0,borderRadius:14,background:'var(--card)',border:'1px solid var(--border)',fontSize:22,color:'var(--text)'}}>→</button>
      <div style={{fontWeight:800,fontSize:15,flex:1}}>{title || 'SectorLand'}</div>
      <div style={{width:42}} />
    </header>
  )
}
