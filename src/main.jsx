import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/global.css'

class AppErrorBoundary extends React.Component {
  constructor(props){super(props);this.state={error:null}}
  static getDerivedStateFromError(error){return {error:error}}
  componentDidCatch(error){
    try{fetch('https://telegram-group-manager-bot-iota.vercel.app/api/miniapp-diagnostic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phase:'react-crash',bridge:Boolean(window.Telegram&&window.Telegram.WebApp),user:false,init:false,version:String(error&&error.message||'').slice(0,80)})})}catch(_){}
  }
  render(){if(!this.state.error)return this.props.children;return <div dir="rtl" style={{minHeight:'100vh',background:'#080b14',color:'#fff',display:'grid',placeItems:'center',padding:24,textAlign:'center'}}><div><div style={{fontSize:52}}>🛠️</div><h2>مینی‌اپ نیاز به تازه‌سازی دارد</h2><p style={{opacity:.7}}>کد تشخیص: REACT-CRASH</p><button onClick={function(){window.location.reload()}} style={{padding:'12px 20px',border:0,borderRadius:12,background:'#2ea6ff',color:'#fff'}}>تلاش دوباره</button></div></div>}
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <AppErrorBoundary><App /></AppErrorBoundary>
)
