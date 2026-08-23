import { useEffect, useState } from 'react'

function readLaunchData(tg) {
  var initData = (tg && tg.initData) || ''

  // Telegram iOS can expose the launch parameters in the URL a few frames
  // before telegram-web-app.js copies them onto WebApp.initData.
  if (!initData) {
    var params = new URLSearchParams(
      (window.location.hash || '').replace(/^#/, '')
    )
    initData = params.get('tgWebAppData') || ''
  }

  var user = tg && tg.initDataUnsafe && tg.initDataUnsafe.user
  if (!user && initData) {
    try {
      var rawUser = new URLSearchParams(initData).get('user')
      if (rawUser) user = JSON.parse(rawUser)
    } catch (_) {}
  }

  return {
    tg: tg || null,
    tgUser: user || null,
    initData: initData,
    colorScheme: (tg && tg.colorScheme) || 'dark',
    launchChecked: Boolean(initData && user),
  }
}

export function useTelegram() {
  var [telegram, setTelegram] = useState(function() {
    return readLaunchData(window.Telegram && window.Telegram.WebApp)
  })

  useEffect(function() {
    var cancelled = false
    var attempts = 0
    var timer

    function syncTelegram() {
      if (cancelled) return
      var tg = window.Telegram && window.Telegram.WebApp
      if (tg) {
        try {
          tg.ready()
          tg.expand()
          tg.enableClosingConfirmation()
        } catch (_) {}
      }

      var next = readLaunchData(tg)
      next.launchChecked = Boolean(next.initData && next.tgUser) || attempts >= 29
      setTelegram(next)

      // Allow the native Telegram bridge time to hydrate on slower iOS opens.
      attempts += 1
      if ((!next.initData || !next.tgUser) && attempts < 30) {
        timer = window.setTimeout(syncTelegram, 100)
      }
    }

    syncTelegram()
    return function() {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [])

  return telegram
}
