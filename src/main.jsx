import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import {API_BASE} from './utils/constants'
import './styles/global.css'
import './styles/sector-v6.css'

function diagnosticHeaders(){
  const initData=window.Telegram?.WebApp?.initData||''
  return {'Content-Type':'application/json',...(initData?{'init-data':initData}:{})}
}

class AppErrorBoundary extends React.Component {
  constructor(props){super(props);this.state={error:null}}
  static getDerivedStateFromError(error){return {error:error}}
  componentDidCatch(error,info){
    console.error('Mini App render failure',error)
    const message=String(error?.message||error).slice(0,500)
    const stack=[String(error?.stack||''),String(info?.componentStack||'')].filter(Boolean).join('\n').slice(0,3500)
    fetch(`${API_BASE}/api/miniapp-diagnostic`,{method:'POST',headers:diagnosticHeaders(),body:JSON.stringify({phase:'react-crash',message,stack,version:'sector-ui-2026.08.25',platform:window.Telegram?.WebApp?.platform||'unknown'})}).catch(()=>{})
  }
  render(){
    if(!this.state.error)return this.props.children
    const code=String(this.state.error?.message||'REACT-CRASH').slice(0,120)
    return <div dir="rtl" style={{minHeight:'100vh',background:'#080b14',color:'#fff',display:'grid',placeItems:'center',padding:24,textAlign:'center'}}><div style={{maxWidth:420}}><img src="/assets/sector/emotions-v3/offline.webp" alt="سکتور آفلاین" style={{display:'block',width:'100%',borderRadius:22}}/><h2>مینی‌اپ نیاز به تازه‌سازی دارد</h2><p>گزارش فنی خطا برای بررسی ثبت شد.</p><p style={{opacity:.7,direction:'ltr',wordBreak:'break-word'}}>کد تشخیص: {code}</p><button onClick={function(){window.location.replace(window.location.pathname+'?refresh='+Date.now())}} style={{padding:'12px 20px',border:0,borderRadius:12,background:'#2ea6ff',color:'#fff'}}>دریافت نسخه جدید</button></div></div>
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <AppErrorBoundary><App /></AppErrorBoundary>
)
