// All runtime config comes from env vars — no hardcoded values
export const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
// Empty string → relative URLs (/api/...) → Vite proxy handles it in dev,
// Nginx/Vercel rewrites handle it in production.

export const BOT_USERNAME     = import.meta.env.VITE_BOT_USERNAME     || 'SectorLandBot'
export const SUPPORT_USERNAME = import.meta.env.VITE_SUPPORT_USERNAME || 'sector_ad'
export const CHANNEL_MAIN     = import.meta.env.VITE_CHANNEL_MAIN     || 'Vaslchannel'
export const CHANNEL_GROUP    = import.meta.env.VITE_CHANNEL_GROUP    || 'Vaslgroupp'
export const CHANNEL_LAND     = import.meta.env.VITE_CHANNEL_LAND     || 'sectorland'

export const NAV_TABS = [
  { key: 'home',    icon: '🏠', label: 'خانه' },
  { key: 'shop',    icon: '🛒', label: 'فروشگاه' },
  { key: 'wallet',  icon: '💰', label: 'کیف پول' },
  { key: 'games',   icon: '🎮', label: 'بازی‌ها' },
  { key: 'profile', icon: '👤', label: 'پروفایل' },
]

// Pages NOT in bottom nav (reached via navigate)
export const SUB_PAGES = ['orders', 'referral', 'support']
