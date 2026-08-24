import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/global.css'

class AppErrorBoundary extends React.Component {
  constructor(props){super(props);this.state={error:null}}
  static getDerivedStateFromError(error){return {error:error}}
  componentDidCatch(error,info){console.error('Mini App render failure',error);fetch('/api/miniapp-diagnostic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phase:'react-crash',message:String(error?.message||error).slice(0,300),stack:String(info?.componentStack||'').slice(0,1200)})}).catch(()=>{})}
  render(){if(!this.state.error)return this.props.children;const code=String(this.state.error?.message||'REACT-CRASH').slice(0,80);return <div dir="rtl" style={{minHeight:'100vh',background:'#080b14',color:'#fff',display:'grid',placeItems:'center',padding:24,textAlign:'center'}}><div style={{maxWidth:420}}><img src="/assets/sector/emotions-v3/offline.webp" alt="سکتور آفلاین" style={{display:'block',width:'100%',borderRadius:22}}/><h2>مینی‌اپ نیاز به تازه‌سازی دارد</h2><p style={{opacity:.7,direction:'ltr'}}>کد تشخیص: {code}</p><button onClick={function(){window.location.replace(window.location.pathname+'?refresh='+Date.now())}} style={{padding:'12px 20px',border:0,borderRadius:12,background:'#2ea6ff',color:'#fff'}}>دریافت نسخه جدید</button></div></div>}
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <AppErrorBoundary><App /></AppErrorBoundary>
)
