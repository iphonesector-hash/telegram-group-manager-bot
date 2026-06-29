import { useEffect } from 'react'

export function useTelegram() {
  const tg = window.Telegram && window.Telegram.WebApp

  useEffect(function() {
    if (tg) {
      tg.ready()
      tg.expand()
      tg.enableClosingConfirmation()
    }
  }, [])

  return {
    tg: tg || null,
    tgUser: tg ? (tg.initDataUnsafe && tg.initDataUnsafe.user) || null : null,
    initData: tg ? tg.initData || '' : '',
    colorScheme: tg ? tg.colorScheme || 'dark' : 'dark',
  }
}
