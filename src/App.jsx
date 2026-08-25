import { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { useTelegram } from './hooks/useTelegram'
import { useToast } from './hooks/useToast'
import { api } from './services/api'
import { haptic, playTone } from './utils/feedback'

import BottomNav from './components/ui/BottomNav'
import Toast from './components/ui/Toast'
import PageHeader from './components/ui/PageHeader'
import SectorBootSplash from './components/ui/SectorBootSplash'

import HomePage    from './pages/HomePage'
import ShopPage    from './pages/ShopPage'
import WalletPage  from './pages/WalletPage'
import GamesPage   from './pages/GamesPage'
import OrdersPage  from './pages/OrdersPage'
import ReferralPage from './pages/ReferralPage'
import ProfilePage from './pages/ProfilePage'
import SupportPage from './pages/SupportPage'
import FeaturesPage from './pages/FeaturesPage'
import AdminPage from './pages/AdminPage'
import ToolsPage from './pages/ToolsPage'
import MissionsPage from './pages/MissionsPage'
import SectorPetPage from './pages/SectorPetPage'
import WhatsNewPage from './pages/WhatsNewPage'
import SettingsPage from './pages/SettingsPage'

var AppContext = createContext(null)
export function useAppContext() { return useContext(AppContext) }

var PAGES = {
  home: HomePage,
  shop: ShopPage,
  wallet: WalletPage,
  games: GamesPage,
  orders: OrdersPage,
  referral: ReferralPage,
  profile: ProfilePage,
  support: SupportPage,
  features: FeaturesPage,
  admin: AdminPage,
  tools: ToolsPage,
  missions: MissionsPage,
  sectorpet: SectorPetPage,
  assets: SectorPetPage,
  whatsnew: WhatsNewPage,
  settings: SettingsPage,
}

var PAGE_TITLES = { shop:'فروشگاه', wallet:'کیف پول و بانک', games:'بازی‌ها و جوایز', profile:'پروفایل', orders:'سفارش‌ها', referral:'دعوت دوستان', support:'پشتیبانی', features:'سایر امکانات', admin:'پنل مدیریت', tools:'ابزارها و دستیار', missions:'ماموریت‌ها', sectorpet:'سکتور کوچولو', assets:'دارایی‌های من', whatsnew:'چه خبر؟', settings:'تنظیمات' }

var EMPTY_USER = {
  id: 0,
  first_name: '',
  username: '',
  coins: 0,
  bank_balance: 0,
  loan_balance: 0,
  xp: 0,
  level: 1,
  rank: 0,
  joined_at: null,
  achievements: [],
  orders_count: 0,
  total_spent: 0,
  referrals: 0,
  is_admin: false,
  unlimited_wallet: false,
  role: 'کاربر',
  correct_answers: 0,
  message_count: 0,
}

function normalizeUser(data) {
  var d = data || {}
  return {
    ...EMPTY_USER,
    ...d,
    coins: Number(d.coins || 0),
    bank_balance: Number(d.bank_balance || 0),
    loan_balance: Number(d.loan_balance || 0),
    xp: Number(d.xp || 0),
    level: Number(d.level || 1),
    rank: Number(d.rank || 0),
    orders_count: Number(d.orders_count || 0),
    total_spent: Number(d.total_spent || 0),
    referrals: Number(d.referrals || 0),
  }
}

export default function App() {
  var telegram = useTelegram()
  var tg = telegram.tg
  var tgUser = telegram.tgUser
  var initData = telegram.initData
  var launchChecked = telegram.launchChecked

  var toastState = useToast()
  var toast = toastState.toast
  var showToast = toastState.showToast

  var [page, setPage] = useState('home')
  var [history, setHistory] = useState([])
  var [dbUser, setDbUser] = useState(EMPTY_USER)
  var [bootLoading, setBootLoading] = useState(true)
  var [membershipAllowed, setMembershipAllowed] = useState(null)
  var [membershipError, setMembershipError] = useState('')
  var [membershipChecking, setMembershipChecking] = useState(false)

  useEffect(function(){
    try{var saved=JSON.parse(localStorage.getItem('sector-ui-settings')||'{}'),root=document.documentElement;root.dataset.motion=saved.motion===false?'off':'on';root.dataset.compact=saved.compact?'on':'off';root.dataset.text=saved.largeText?'large':'normal';root.dataset.dataSaver=saved.dataSaver?'on':'off'}catch(_){}
  },[])

  var navigate = useCallback(function(to) {
    if (to === page) return
    haptic(tg, 'light')
    setHistory(function(items) { return items.concat(page).slice(-12) })
    setPage(to)
  }, [page, tg])

  var goBack = useCallback(function() {
    haptic(tg, 'light')
    setHistory(function(items) {
      var next = items.length ? items[items.length - 1] : 'home'
      setPage(next)
      return items.slice(0, -1)
    })
  }, [tg])

  useEffect(function() {
    if (!tg) return
    if (page !== 'home') {
      tg.BackButton.show()
      tg.BackButton.onClick(goBack)
    } else {
      tg.BackButton.hide()
    }
    return function() {
      try { tg.BackButton.offClick(goBack) } catch (_) {}
    }
  }, [page, tg, goBack])

  var loadUserAfterMembership = useCallback(function() {
    if (!tgUser || !initData) return Promise.resolve(false)
    return api.getUser(tgUser.id, initData).then(function(result) {
      if (result && result.data && result.data.id) {
        setDbUser(normalizeUser(result.data))
        return true
      }
      showToast('اطلاعات حساب از ربات دریافت نشد', 'error')
      return false
    })
  }, [tgUser, initData, showToast])

  var checkMembership = useCallback(function(options) {
    if (!tgUser || !initData) return Promise.resolve(false)
    var opts = options || {}
    if (opts.interactive) setMembershipChecking(true)
    setMembershipError('')
    return api.getMembership(tgUser.id, initData).then(function(membershipResult) {
      if (!membershipResult || !membershipResult.data) {
        setMembershipAllowed(false)
        setMembershipError((membershipResult && membershipResult.error) || 'ارتباط با سرور بررسی عضویت برقرار نشد؛ دوباره تلاش کن.')
        return false
      }
      if (!membershipResult.data.member) {
        setMembershipAllowed(false)
        setMembershipError('برای استفاده از Mini App باید عضو @sectorland باشی.')
        return false
      }
      setMembershipAllowed(true)
      return loadUserAfterMembership()
    }).catch(function() {
      setMembershipAllowed(false)
      setMembershipError('بررسی عضویت موقتاً در دسترس نیست.')
      return false
    }).finally(function() {
      if (opts.interactive) setMembershipChecking(false)
    })
  }, [tgUser, initData, loadUserAfterMembership])

  useEffect(function() {
    var active = true
    var safetyTimer = window.setTimeout(function() {
      if (active) {
        setBootLoading(false)
        setMembershipError('اتصال کند است؛ دوباره تلاش کن.')
      }
    }, 8000)
    if (!tgUser || !initData) {
      if (!launchChecked) return function() { active = false; window.clearTimeout(safetyTimer) }
      setBootLoading(false)
      window.clearTimeout(safetyTimer)
      return function() { active = false }
    }

    checkMembership().finally(function() {
      if (!active) return
      setBootLoading(false)
      window.clearTimeout(safetyTimer)
    })

    api.getUserPhoto(tgUser.id, initData).then(function(photoResult) {
      if (!active) return
      var photoUrl = photoResult && photoResult.data && photoResult.data.photo_url
      if (photoUrl && telegram.setPhotoUrl) telegram.setPhotoUrl(photoUrl)
    })
    return function() { active = false; window.clearTimeout(safetyTimer) }
  }, [tgUser, initData, launchChecked, checkMembership])

  var apiCall = useCallback(function(method) {
    var args = Array.prototype.slice.call(arguments, 1)
    args.push(initData)
    return api[method].apply(api, args).then(function(result){
      var payload=result&&result.data
      if(payload&&payload.coins!==undefined){
        setDbUser(function(user){return {...user,coins:Number(payload.coins||0)}})
      } else if(payload&&payload.pet&&payload.pet.coins!==undefined){
        setDbUser(function(user){return {...user,coins:Number(payload.pet.coins||0)}})
      }
      return result
    })
  }, [initData])

  var refreshUser = useCallback(function() {
    if (!tgUser || !initData) return Promise.resolve(null)
    return api.getUser(tgUser.id, initData).then(function(result) {
      if (result && result.data && result.data.id) {
        var normalized = normalizeUser(result.data)
        setDbUser(normalized)
        return normalized
      }
      return null
    })
  }, [tgUser, initData])

  var ctx = {
    tg: tg,
    tgUser: tgUser,
    initData: initData,
    dbUser: dbUser,
    setDbUser: setDbUser,
    refreshUser: refreshUser,
    page: page,
    navigate: navigate,
    goBack: goBack,
    showToast: showToast,
    apiCall: apiCall,
  }

  if (bootLoading) return <SectorBootSplash />

  if (!tgUser) {
    return (
      <div style={{height:'100dvh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:16,padding:24,background:'var(--bg)',textAlign:'center'}}>
        <div style={{ fontSize: 56 }}>🔒</div>
        <div style={{ fontWeight: 800, fontSize: 20 }}>فقط داخل تلگرام</div>
        <div style={{ color: 'var(--muted)', fontSize: 14, lineHeight: 1.7 }}>
          لطفاً این اپ رو از داخل تلگرام باز کنید.<br />از طریق بات @iSectorlandbot وارد بشید.
        </div>
        <button className="btn btn-primary" onClick={function(){window.location.reload()}}>🔄 تلاش دوباره</button>
        <a className="btn btn-gold" href="https://t.me/iSectorlandbot?start=miniapp" style={{textDecoration:'none'}}>🤖 باز کردن ربات</a>
        <div style={{fontSize:10,color:'var(--muted)'}}>کد تشخیص: {telegram.tg?'TG-NO-USER':'NO-TG-BRIDGE'}</div>
      </div>
    )
  }

  if (membershipAllowed !== true) {
    return (
      <div style={{height:'100dvh',display:'flex',alignItems:'center',justifyContent:'center',padding:22,background:'radial-gradient(circle at 50% 15%,rgba(79,123,255,.18),transparent 40%),var(--bg)',textAlign:'center'}}>
        <div className="glass" style={{width:'100%',maxWidth:380,padding:'24px 20px'}}>
          <img src="/assets/sector/koochooloo-hero-v2.webp" alt="SectorLand" style={{width:'100%',borderRadius:16,marginBottom:16}} />
          <div style={{fontSize:22,fontWeight:900,marginBottom:8}}>🔒 عضویت در SectorLand الزامی است</div>
          <div style={{fontSize:13,color:'var(--muted)',lineHeight:1.9,marginBottom:18}}>{membershipError || 'ابتدا عضو کانال اصلی SectorLand شو و بعد دوباره بررسی کن.'}</div>
          <a className="btn btn-primary" href="https://t.me/sectorland" style={{textDecoration:'none',marginBottom:10}}>📣 عضویت در @sectorland</a>
          <button className="btn btn-gold" disabled={membershipChecking} onClick={function(){checkMembership({interactive:true})}} style={{width:'100%',opacity:membershipChecking?0.65:1}}>{membershipChecking?'⏳ در حال بررسی…':'✅ عضو شدم — بررسی کن'}</button>
        </div>
      </div>
    )
  }

  var PageComponent = PAGES[page] || PAGES.home
  return (
    <AppContext.Provider value={ctx}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh' }} onPointerDownCapture={function(event){var button=event.target.closest&&event.target.closest('button,a');if(button&&!button.disabled)playTone('tap')}}>
        {page !== 'home' && <PageHeader title={PAGE_TITLES[page]} onBack={goBack} />}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }} key={page}>
          <PageComponent />
        </div>
        <BottomNav page={page} onNavigate={navigate} isAdmin={dbUser.is_admin} />
        <Toast toast={toast} />
      </div>
    </AppContext.Provider>
  )
}
