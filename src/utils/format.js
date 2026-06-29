/** Format a number with Persian locale */
export const fNum = (n) =>
  typeof n === 'number' ? n.toLocaleString('fa-IR') : (n ?? '—')

/** Format coin amount with icon */
export const fCoins = (n) => `${fNum(n)} 🪙`

/** Format toman amount */
export const fToman = (n) => `${fNum(n)} تومان`

/** Clamp a progress % between 0–100 */
export const clampPct = (val, max) =>
  Math.min(100, Math.max(0, Math.round((val / max) * 100)))

/** Telegram initData safe accessor */
export const getTgUser = () =>
  window.Telegram?.WebApp?.initDataUnsafe?.user ?? null
