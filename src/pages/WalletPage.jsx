import { useEffect, useState } from 'react'
import { useAppContext } from '../App'

function formatDate(value) {
  if (!value) return '—'
  try { return new Date(value).toLocaleDateString('fa-IR') } catch (_) { return '—' }
}

export default function WalletPage() {
  var ctx = useAppContext()
  var dbUser = ctx.dbUser
  var navigate = ctx.navigate
  var apiCall = ctx.apiCall
  var tgUser = ctx.tgUser
  var [tab, setTab] = useState('overview')
  var [transactions, setTransactions] = useState([])
  var [loadingTx, setLoadingTx] = useState(false)

  var coins = Number(dbUser.coins || 0)
  var bankBalance = Number(dbUser.bank_balance || 0)
  var loanBalance = Number(dbUser.loan_balance || 0)
  var xp = Number(dbUser.xp || 0)
  var level = Number(dbUser.level || 1)

  useEffect(function() {
    if (tab !== 'history' || !tgUser) return
    setLoadingTx(true)
    apiCall('getTransactions', tgUser.id).then(function(result) {
      setTransactions(Array.isArray(result && result.data) ? result.data : [])
      setLoadingTx(false)
    })
  }, [tab, tgUser, apiCall])

  var tabs = [
    { key: 'overview', label: '📋 خلاصه' },
    { key: 'history', label: '📜 تاریخچه' },
  ]

  return (
    <div className="page fade-up">
      <div className="sec-title">💰 کیف پول</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 18 }}>
        <div className="glass" style={{ padding: '18px 14px', background: 'linear-gradient(135deg,rgba(245,200,66,.15),rgba(240,158,25,.06))' }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>سکه‌های من</div>
          <div style={{ fontWeight: 800, fontSize: 26, color: 'var(--gold)' }}>{coins.toLocaleString()}</div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>🪙 سکه</div>
        </div>
        <div className="glass" style={{ padding: '18px 14px', background: 'linear-gradient(135deg,rgba(34,216,122,.12),rgba(34,216,122,.03))' }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>موجودی بانک</div>
          <div style={{ fontWeight: 800, fontSize: 26, color: 'var(--green)' }}>{bankBalance.toLocaleString()}</div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>🏦 سکه</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 20 }}>
        {[
          { icon: '🛒', label: 'فروشگاه', fn: function() { navigate('shop') } },
          { icon: '📊', label: 'تراکنش‌ها', fn: function() { setTab('history') } },
          { icon: '🎁', label: 'جوایز', fn: function() { navigate('games') } },
        ].map(function(a, i) {
          return <button key={i} onClick={a.fn} className="glass btn" style={{ flexDirection:'column', gap:6, padding:'14px 8px', border:'1px solid var(--border)', cursor:'pointer' }}><span style={{fontSize:22}}>{a.icon}</span><span style={{fontSize:11,fontWeight:600,color:'var(--muted)'}}>{a.label}</span></button>
        })}
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {tabs.map(function(t) {
          return <button key={t.key} onClick={function(){setTab(t.key)}} className="btn btn-sm" style={{ background:tab===t.key?'linear-gradient(135deg,var(--accent),var(--accent2))':'var(--card)', color:tab===t.key?'#fff':'var(--muted)', border:tab===t.key?'none':'1px solid var(--border)' }}>{t.label}</button>
        })}
      </div>

      {tab === 'overview' && (
        <div className="glass" style={{ padding: '16px' }}>
          <div style={{ color: 'var(--muted)', fontSize: 12, marginBottom: 12 }}>اطلاعات واقعی حساب ربات</div>
          {[
            { label:'بدهی وام', val:loanBalance.toLocaleString()+' سکه', icon:'💳' },
            { label:'XP', val:xp.toLocaleString(), icon:'⭐' },
            { label:'سطح', val:level.toLocaleString('fa-IR'), icon:'🏅' },
            { label:'رتبه', val:dbUser.rank?'#'+Number(dbUser.rank).toLocaleString('fa-IR'):'—', icon:'🏆' },
            { label:'تعداد سفارش', val:Number(dbUser.orders_count||0).toLocaleString('fa-IR'), icon:'📦' },
          ].map(function(s, i) {
            return <div key={i} style={{display:'flex',justifyContent:'space-between',padding:'10px 0',borderBottom:i<4?'1px solid var(--border)':'none'}}><span style={{color:'var(--muted)',fontSize:13}}>{s.icon} {s.label}</span><span style={{fontWeight:600,fontSize:13}}>{s.val}</span></div>
          })}
        </div>
      )}

      {tab === 'history' && (
        <div className="glass" style={{ overflow: 'hidden' }}>
          {loadingTx && <div style={{padding:20,textAlign:'center',color:'var(--muted)'}}>در حال دریافت تراکنش‌ها...</div>}
          {!loadingTx && transactions.length === 0 && <div style={{padding:20,textAlign:'center',color:'var(--muted)'}}>هنوز تراکنش واقعی ثبت نشده.</div>}
          {!loadingTx && transactions.map(function(tx, i) {
            return <div key={tx.id} style={{display:'flex',alignItems:'center',gap:12,padding:'13px 16px',borderBottom:i<transactions.length-1?'1px solid var(--border)':'none'}}>
              <div style={{width:38,height:38,borderRadius:'50%',background:Number(tx.amount)<0?'rgba(255,79,106,.12)':'rgba(34,216,122,.12)',display:'flex',alignItems:'center',justifyContent:'center'}}>{Number(tx.amount)<0?'⬇️':'⬆️'}</div>
              <div style={{flex:1}}><div style={{fontSize:13,fontWeight:600}}>{tx.label}</div><div style={{fontSize:11,color:'var(--muted)'}}>{formatDate(tx.date)}</div></div>
              <div style={{fontWeight:700,color:Number(tx.amount)<0?'var(--red)':'var(--green)'}}>{Number(tx.amount)>0?'+':''}{Number(tx.amount).toLocaleString()} 🪙</div>
            </div>
          })}
        </div>
      )}
    </div>
  )
}
