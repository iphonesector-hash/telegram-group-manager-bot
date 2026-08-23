import { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { useTelegram } from './hooks/useTelegram'
import { useToast } from './hooks/useToast'
import { api } from './services/api'
import { NAV_ITEMS } from './utils/mock'

import BottomNav from './components/ui/BottomNav'
import Toast from './components/ui/Toast'
import PageHeader from './components/ui/PageHeader'

import HomePage    from './pages/HomePage'
import ShopPage    from './pages/ShopPage'
import WalletPage  from './pages/WalletPage'
import GamesPage   from './pages/GamesPage'
import OrdersPage  from './pages/OrdersPage'
import ReferralPage from './pages/ReferralPage'
import ProfilePage from './pages/ProfilePage'
import SupportPage from './pages/SupportPage'
import FeaturesPage from './pages/FeaturesPage'

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
}

var NAV_KEYS = NAV_ITEMS.map(function(n) { return n.key })
var PAGE_TITLES = { shop:'فروشگاه', wallet:'کیف پول و بانک', games:'بازی‌ها و جوایز', profile:'پروفایل', orders:'سفارش‌ها', referral:'دعوت دوستان', support:'پشتیبانی', features:'امکانات ربات' }

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

  var navigate = useCallback(function(to) {
    if (to === page) return
    setHistory(function(items) { return items.concat(page).slice(-12) })
    setPage(to)
  }, [page])

  var goBack = useCallback(function() {
    setHistory(function(items) {
      var next = items.length ? items[items.length - 1] : 'home'
      setPage(next)
      return items.slice(0, -1)
    })
  }, [])

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

  useEffect(function() {
    if (!tgUser || !initData) {
      if (!launchChecked) return
      setBootLoading(false)
      return
    }
    api.getUser(tgUser.id, initData).then(function(result) {
      if (result && result.data && result.data.id) {
        setDbUser(normalizeUser(result.data))
      } else {
        showToast('اطلاعات حساب از ربات دریافت نشد', 'error')
      }
      setBootLoading(false)
    })
    api.getUserPhoto(tgUser.id, initData).then(function(photoResult) {
      var photoUrl = photoResult && photoResult.data && photoResult.data.photo_url
      if (photoUrl && telegram.setPhotoUrl) telegram.setPhotoUrl(photoUrl)
    })
  }, [tgUser, initData, launchChecked, showToast])

  var apiCall = useCallback(function(method) {
    var args = Array.prototype.slice.call(arguments, 1)
    args.push(initData)
    return api[method].apply(api, args)
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

  if (bootLoading) {
    return (
      <div style={{height:'100vh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:20,background:'var(--bg)'}}>
        <div style={{ fontSize: 52 }}>🌐</div>
        <div className="spinner" />
        <div style={{ color: 'var(--muted)', fontSize: 14 }}>SectorLand در حال بارگذاری...</div>
      </div>
    )
  }

  if (!tgUser) {
    return (
      <div style={{height:'100vh',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:16,padding:24,background:'var(--bg)',textAlign:'center'}}>
        <div style={{ fontSize: 56 }}>🔒</div>
        <div style={{ fontWeight: 800, fontSize: 20 }}>فقط داخل تلگرام</div>
        <div style={{ color: 'var(--muted)', fontSize: 14, lineHeight: 1.7 }}>
          لطفاً این اپ رو از داخل تلگرام باز کنید.<br />از طریق بات @iSectorlandbot وارد بشید.
        </div>
      </div>
    )
  }

  var PageComponent = PAGES[page] || PAGES.home
  var showNav = NAV_KEYS.indexOf(page) !== -1

  return (
    <AppContext.Provider value={ctx}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {page !== 'home' && <PageHeader title={PAGE_TITLES[page]} onBack={goBack} />}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }} key={page}>
          <PageComponent />
        </div>
        {showNav && <BottomNav page={page} onNavigate={navigate} />}
        <Toast toast={toast} />
      </div>
    </AppContext.Provider>
  )
}
