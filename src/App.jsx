import { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { useTelegram } from './hooks/useTelegram'
import { useToast } from './hooks/useToast'
import { api } from './services/api'
import { MOCK_USER, NAV_ITEMS } from './utils/mock'

import BottomNav from './components/ui/BottomNav'
import Toast from './components/ui/Toast'

import HomePage    from './pages/HomePage'
import ShopPage    from './pages/ShopPage'
import WalletPage  from './pages/WalletPage'
import GamesPage   from './pages/GamesPage'
import OrdersPage  from './pages/OrdersPage'
import ReferralPage from './pages/ReferralPage'
import ProfilePage from './pages/ProfilePage'
import SupportPage from './pages/SupportPage'

// ── App Context ──────────────────────────────────────────────────────
var AppContext = createContext(null)
export function useAppContext() { return useContext(AppContext) }

// ── Page registry ───────────────────────────────────────────────────
var PAGES = {
  home:     HomePage,
  shop:     ShopPage,
  wallet:   WalletPage,
  games:    GamesPage,
  orders:   OrdersPage,
  referral: ReferralPage,
  profile:  ProfilePage,
  support:  SupportPage,
}

var NAV_KEYS = NAV_ITEMS.map(function(n) { return n.key })

export default function App() {
  var telegram = useTelegram()
  var tg = telegram.tg
  var tgUser = telegram.tgUser
  var initData = telegram.initData

  var toastState = useToast()
  var toast = toastState.toast
  var showToast = toastState.showToast

  var [page, setPage]         = useState('home')
  var [prevPage, setPrevPage] = useState('home')
  var [dbUser, setDbUser]     = useState(MOCK_USER)
  var [bootLoading, setBootLoading] = useState(true)

  // Navigate helper
  var navigate = useCallback(function(to) {
    setPrevPage(page)
    setPage(to)
  }, [page])

  // Telegram BackButton
  useEffect(function() {
    if (!tg) return
    var isMain = NAV_KEYS.indexOf(page) !== -1
    if (!isMain) {
      tg.BackButton.show()
      tg.BackButton.onClick(function() {
        setPage(prevPage || 'home')
      })
    } else {
      tg.BackButton.hide()
    }
  }, [page, prevPage, tg])

  // Initial user load from API — falls back to MOCK_USER if API is down
  useEffect(function() {
    if (!tgUser) { setBootLoading(false); return }
    api.getUser(tgUser.id, initData).then(function(result) {
      if (result && result.data && result.data.id) {
        setDbUser(function(prev) { return Object.assign({}, prev, result.data) })
      }
      setBootLoading(false)
    })
  }, [tgUser, initData])

  // Unified API caller passed via context
  var apiCall = useCallback(function(method) {
    var args = Array.prototype.slice.call(arguments, 1)
    args.push(initData)
    return api[method].apply(api, args)
  }, [initData])

  // Context value
  var ctx = {
    tgUser:   tgUser,
    initData: initData,
    dbUser:   dbUser,
    setDbUser: setDbUser,
    page:     page,
    navigate: navigate,
    showToast: showToast,
    apiCall:  apiCall,
  }

  // ── Boot loading screen
  if (bootLoading) {
    return (
      <div style={{
        height: '100vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        gap: 20, background: 'var(--bg)'
      }}>
        <div style={{ fontSize: 52 }}>🌐</div>
        <div className="spinner" />
        <div style={{ color: 'var(--muted)', fontSize: 14 }}>SectorLand در حال بارگذاری...</div>
      </div>
    )
  }

  // ── No Telegram context
  if (!tgUser) {
    return (
      <div style={{
        height: '100vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        gap: 16, padding: 24, background: 'var(--bg)', textAlign: 'center'
      }}>
        <div style={{ fontSize: 56 }}>🔒</div>
        <div style={{ fontWeight: 800, fontSize: 20 }}>فقط داخل تلگرام</div>
        <div style={{ color: 'var(--muted)', fontSize: 14, lineHeight: 1.7 }}>
          لطفاً این اپ رو از داخل تلگرام باز کنید.
          <br />از طریق بات @SectorLandBot وارد بشید.
        </div>
        <a href="https://t.me/SectorLandBot"
          className="btn btn-primary"
          style={{ textDecoration: 'none', padding: '12px 30px', borderRadius: 12, marginTop: 8, width: 'auto' }}>
          باز کردن در تلگرام
        </a>
      </div>
    )
  }

  var PageComponent = PAGES[page] || PAGES['home']
  var showNav = NAV_KEYS.indexOf(page) !== -1

  return (
    <AppContext.Provider value={ctx}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>

        {/* Page */}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
          key={page}>
          <PageComponent />
        </div>

        {/* Bottom Nav — only for main tabs */}
        {showNav && (
          <BottomNav page={page} onNavigate={navigate} />
        )}

        {/* Toast */}
        <Toast toast={toast} />
      </div>
    </AppContext.Provider>
  )
}
