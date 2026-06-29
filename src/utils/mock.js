// ═══════════════════════════════════════════════
// Mock / fallback data — used when API is unavailable
// Replace with real backend responses in production
// ═══════════════════════════════════════════════

export const MOCK_USER = {
  id: 0,
  coins: 2450,
  bank: 15000,
  level: 7,
  xp: 680,
  xpNext: 1000,
  rank: 12,
  totalSpent: 320000,
  memberSince: 'اردیبهشت ۱۴۰۳',
  referrals: 8,
}

export const MOCK_PRODUCTS = [
  {
    id: 1, name: 'VPN اقتصادی', price: 120000, coins: 0,
    duration: '۱ ماه', category: 'vpn',
    features: ['۵ دستگاه', 'سرعت متوسط', 'پشتیبانی پایه'],
    badge: 'پرفروش', color: '#4f7bff',
  },
  {
    id: 2, name: 'VPN حرفه‌ای', price: 280000, coins: 0,
    duration: '۳ ماه', category: 'vpn',
    features: ['نامحدود دستگاه', 'سرعت بالا', 'پشتیبانی ۲۴/۷', 'IP ثابت'],
    badge: 'ویژه', color: '#a259ff',
  },
  {
    id: 3, name: 'VPN آنلیمیتد', price: 480000, coins: 0,
    duration: '۶ ماه', category: 'vpn',
    features: ['همه چیز آنلیمیتد', 'سرعت نامحدود', 'SLA 99.9%', 'IP اختصاصی'],
    badge: 'بهترین', color: '#f5c842',
  },
  {
    id: 4, name: 'سکه ۵۰۰ تایی', price: 50000, coins: 500,
    duration: '—', category: 'coins',
    features: ['واریز فوری', 'بدون انقضا', 'قابل هدیه'],
    badge: '', color: '#22d87a',
  },
  {
    id: 5, name: 'سکه ۱۵۰۰ تایی', price: 130000, coins: 1500,
    duration: '—', category: 'coins',
    features: ['واریز فوری', 'بدون انقضا', '۱۵٪ هدیه اضافه'],
    badge: 'صرفه‌جو', color: '#22d87a',
  },
]

export const MOCK_TRANSACTIONS = [
  { id: 1, type: 'earn',  label: 'هدیه روزانه',       amount: +50,   date: 'امروز ۱۲:۳۰' },
  { id: 2, type: 'spend', label: 'خرید VPN اقتصادی',   amount: -120,  date: 'دیروز' },
  { id: 3, type: 'earn',  label: 'پاداش معرفی',        amount: +200,  date: '۳ روز پیش' },
  { id: 4, type: 'earn',  label: 'هدیه روزانه',        amount: +50,   date: '۴ روز پیش' },
  { id: 5, type: 'spend', label: 'خرید سکه',           amount: -500,  date: '۱ هفته پیش' },
]

export const MOCK_ORDERS = [
  { id: 1, name: 'VPN حرفه‌ای', status: 'active',  expires: '۱۴۰۳/۱۰/۱۵', daysLeft: 47 },
  { id: 2, name: 'VPN اقتصادی', status: 'expired', expires: '۱۴۰۳/۰۷/۰۱', daysLeft: 0 },
]

export const MOCK_LEADERBOARD = [
  { rank: 1,  name: 'علی م.',    coins: 12400, level: 18, badge: '👑' },
  { rank: 2,  name: 'رضا ک.',    coins: 9800,  level: 15, badge: '🥈' },
  { rank: 3,  name: 'فاطمه ن.', coins: 8200,  level: 14, badge: '🥉' },
  { rank: 4,  name: 'حسین ع.',  coins: 7100,  level: 12, badge: '' },
  { rank: 5,  name: 'زهرا م.',  coins: 6600,  level: 11, badge: '' },
  { rank: 6,  name: 'محمد ر.',  coins: 5900,  level: 10, badge: '' },
  { rank: 7,  name: 'نرگس ت.',  coins: 5200,  level: 9,  badge: '' },
  { rank: 8,  name: 'امیر ش.',  coins: 4800,  level: 9,  badge: '' },
  { rank: 9,  name: 'مریم ب.',  coins: 4100,  level: 8,  badge: '' },
  { rank: 10, name: 'سارا ح.',  coins: 3700,  level: 7,  badge: '' },
]

export const MOCK_MISSIONS = [
  { id: 1, title: 'ورود روزانه',     desc: 'هر روز وارد اپ شو',          reward: 50,   done: true,  progress: 1,    total: 1 },
  { id: 2, title: 'خرید اول',        desc: 'اولین خریدت رو ثبت کن',      reward: 200,  done: true,  progress: 1,    total: 1 },
  { id: 3, title: 'معرفی دوستان',   desc: '۵ نفر رو دعوت کن',           reward: 500,  done: false, progress: 3,    total: 5 },
  { id: 4, title: 'سکه‌دار بزرگ',   desc: '۵۰۰۰ سکه جمع‌آوری کن',      reward: 1000, done: false, progress: 2450, total: 5000 },
  { id: 5, title: 'مشتری وفادار',   desc: '۳ بار خرید کن',              reward: 300,  done: false, progress: 1,    total: 3 },
]

export const MOCK_FAQ = [
  { q: 'چطور VPN رو فعال کنم؟',       a: 'بعد از خرید، اطلاعات اتصال به پیام تلگرامت ارسال می‌شه. دستورالعمل کامل داخل پیام هست.' },
  { q: 'چند دستگاه می‌تونم وصل کنم؟', a: 'بسته به پلن انتخابی شما متفاوته. پلن اقتصادی ۵ دستگاه، پلن حرفه‌ای و آنلیمیتد نامحدود.' },
  { q: 'سرعت اتصال چقدره؟',            a: 'سرعت به پلن و سرور انتخابی بستگی داره. پلن آنلیمیتد تا ۱ گیگ برای هر سرور دسترسی داره.' },
  { q: 'پشتیبانی چطوری انجام می‌شه؟',  a: 'از طریق تیکت داخل اپ یا ارسال پیام به @sector_ad در تلگرام.' },
  { q: 'آیا می‌تونم پلنم رو ارتقا بدم؟', a: 'بله، قبل از انقضا می‌تونی پلن بالاتر رو خریداری کنی.' },
]

export const WHEEL_PRIZES = [
  { label: '🎁 ۵۰ سکه',   coins: 50 },
  { label: '💎 ۲۰۰ سکه',  coins: 200 },
  { label: '⭐ ۱۰۰ سکه',  coins: 100 },
  { label: '🎰 ۵۰۰ سکه',  coins: 500 },
  { label: '🪙 ۲۵ سکه',   coins: 25 },
  { label: '🏆 ۱۰۰۰ سکه', coins: 1000 },
  { label: '🎯 ۷۵ سکه',   coins: 75 },
  { label: '💫 ۱۵۰ سکه',  coins: 150 },
]

export const WHEEL_COLORS = [
  '#4f7bff', '#a259ff', '#22d87a', '#f5c842',
  '#ff4f6a', '#00c9ff', '#ff8040', '#ff4fd8',
]

export const NAV_ITEMS = [
  { key: 'home',    icon: '🏠', label: 'خانه' },
  { key: 'shop',    icon: '🛒', label: 'فروشگاه' },
  { key: 'wallet',  icon: '💰', label: 'کیف پول' },
  { key: 'games',   icon: '🎮', label: 'بازی‌ها' },
  { key: 'profile', icon: '👤', label: 'پروفایل' },
]
