import { useEffect, useState } from 'react'
import { useAppContext } from '../App'

function formatDate(value) {
  if (!value) return '—'
  try { return new Date(value).toLocaleString('fa-IR') } catch (_) { return '—' }
}

export default function WalletPage() {
  var ctx = useAppContext()
  var dbUser = ctx.dbUser
  var setDbUser = ctx.setDbUser
  var navigate = ctx.navigate
  var apiCall = ctx.apiCall
  var tgUser = ctx.tgUser
  var showToast = ctx.showToast
  var [tab, setTab] = useState('overview')
  var [transactions, setTransactions] = useState([])
  var [loadingTx, setLoadingTx] = useState(false)
  var [busy, setBusy] = useState(false)

  var coins = Number(dbUser.coins || 0)
  var bankBalance = Number(dbUser.bank_balance || 0)
  var loanBalance = Number(dbUser.loan_balance || 0)
  var xp = Number(dbUser.xp || 0)
  var level = Number(dbUser.level || 1)

  function refreshTransactions() {
    if (!tgUser) return
    setLoadingTx(true)
    apiCall('getTransactions', tgUser.id).then(function(result) {
      setTransactions(Array.isArray(result && result.data) ? result.data : [])
      setLoadingTx(false)
    })
  }

  useEffect(function() {
    if (tab === 'history') refreshTransactions()
  }, [tab, tgUser])

  function runBankAction(action, amount) {
    if (!tgUser || busy) return
    setBusy(true)
    apiCall('bankAction', tgUser.id, action, amount).then(function(result) {
      var data = result && result.data
      if (data && data.status === 'success') {
        setDbUser(function(u) { return { ...u, coins:data.coins, bank_balance:data.bank_balance, loan_balance:data.loan_balance } })
        showToast('✅ عملیات بانکی ثبت شد.', 'success')
        if (tab === 'history') refreshTransactions()
      } else {
        showToast((data && data.message) || 'عملیات بانکی انجام نشد.', 'error')
      }
      setBusy(false)
    })
  }

  var tabs = [
    { key: 'overview', label: '📋 خلاصه' },
    { key: 'history', label: '📜 تاریخچه' },
  ]

  return (
    <div className="page fade-up">
      <div className="sec-title">💰 کیف پول و بانک</div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginBottom:12 }}>
        <div className="glass" style={{ padding:'18px 14px', background:'linear-gradient(135deg,rgba(245,200,66,.15),rgba(240,158,25,.06))' }}><div style={{fontSize:11,color:'var(--muted)'}}>سکه‌های من</div><div style={{fontWeight:800,fontSize:26,color:'var(--gold)'}}>{coins.toLocaleString()}</div><div style={{fontSize:11,color:'var(--muted)'}}>🪙 سکه</div></div>
        <div className="glass" style={{ padding:'18px 14px', background:'linear-gradient(135deg,rgba(34,216,122,.12),rgba(34,216,122,.03))' }}><div style={{fontSize:11,color:'var(--muted)'}}>موجودی بانک</div><div style={{fontWeight:800,fontSize:26,color:'var(--green)'}}>{bankBalance.toLocaleString()}</div><div style={{fontSize:11,color:'var(--muted)'}}>🏦 سکه</div></div>
      </div>

      <div className="glass" style={{padding:'12px 14px',marginBottom:12,display:'flex',justifyContent:'space-between'}}><span style={{color:'var(--muted)',fontSize:12}}>بدهی وام</span><span style={{fontWeight:800,color:loanBalance>0?'var(--red)':'var(--green)'}}>{loanBalance.toLocaleString()} 🪙</span></div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:18}}>
        <button disabled={busy} onClick={function(){runBankAction('deposit',100)}} className="btn btn-primary">⬆️ واریز ۱۰۰</button>
        <button disabled={busy} onClick={function(){runBankAction('withdraw',100)}} className="btn">⬇️ برداشت ۱۰۰</button>
        <button disabled={busy || loanBalance>0} onClick={function(){runBankAction('loan',200)}} className="btn">🏦 وام ۲۰۰</button>
        <button disabled={busy || loanBalance<=0} onClick={function(){runBankAction('repay',0)}} className="btn">📉 تسویه وام</button>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8,marginBottom:20}}>{[
        {icon:'🛒',label:'فروشگاه',fn:function(){navigate('shop')}},{icon:'📊',label:'تراکنش‌ها',fn:function(){setTab('history')}},{icon:'🎁',label:'جوایز',fn:function(){navigate('games')}}
      ].map(function(a,i){return <button key={i} onClick={a.fn} className="glass btn" style={{flexDirection:'column',gap:6,padding:'14px 8px',border:'1px solid var(--border)'}}><span style={{fontSize:22}}>{a.icon}</span><span style={{fontSize:11,fontWeight:600,color:'var(--muted)'}}>{a.label}</span></button>})}</div>

      <div style={{display:'flex',gap:8,marginBottom:16}}>{tabs.map(function(t){return <button key={t.key} onClick={function(){setTab(t.key)}} className="btn btn-sm" style={{background:tab===t.key?'linear-gradient(135deg,var(--accent),var(--accent2))':'var(--card)',color:tab===t.key?'#fff':'var(--muted)',border:tab===t.key?'none':'1px solid var(--border)'}}>{t.label}</button>})}</div>

      {tab==='overview' && <div className="glass" style={{padding:16}}><div style={{color:'var(--muted)',fontSize:12,marginBottom:12}}>اطلاعات واقعی حساب ربات</div>{[
        {label:'XP',val:xp.toLocaleString(),icon:'⭐'},{label:'سطح',val:level.toLocaleString('fa-IR'),icon:'🏅'},{label:'رتبه',val:dbUser.rank?'#'+Number(dbUser.rank).toLocaleString('fa-IR'):'—',icon:'🏆'},{label:'تعداد سفارش',val:Number(dbUser.orders_count||0).toLocaleString('fa-IR'),icon:'📦'}
      ].map(function(s,i){return <div key={i} style={{display:'flex',justifyContent:'space-between',padding:'10px 0',borderBottom:i<3?'1px solid var(--border)':'none'}}><span style={{color:'var(--muted)',fontSize:13}}>{s.icon} {s.label}</span><span style={{fontWeight:600,fontSize:13}}>{s.val}</span></div>})}</div>}

      {tab==='history' && <div className="glass" style={{overflow:'hidden'}}>{loadingTx && <div style={{padding:20,textAlign:'center',color:'var(--muted)'}}>در حال دریافت تراکنش‌ها...</div>}{!loadingTx && transactions.length===0 && <div style={{padding:20,textAlign:'center',color:'var(--muted)'}}>هنوز تراکنشی ثبت نشده.</div>}{!loadingTx && transactions.map(function(tx,i){var earn=Number(tx.amount)>=0;return <div key={tx.id||i} style={{display:'flex',alignItems:'center',gap:12,padding:'13px 16px',borderBottom:i<transactions.length-1?'1px solid var(--border)':'none'}}><div style={{width:44,height:38,borderRadius:11,background:earn?'rgba(34,216,122,.12)':'rgba(255,79,106,.12)',display:'grid',placeItems:'center',fontSize:9,color:earn?'var(--green)':'var(--red)'}}>{tx.direction||(earn?'ورودی':'خروجی')}</div><div style={{flex:1}}><div style={{fontSize:13,fontWeight:600}}>{tx.label}</div><div style={{fontSize:11,color:'var(--muted)'}}>{formatDate(tx.date)}</div></div><div style={{fontWeight:700,color:earn?'var(--green)':'var(--red)'}}>{earn?'+':''}{Number(tx.amount||0).toLocaleString('fa-IR')} سکه</div></div>})}</div>}
    </div>
  )
}
