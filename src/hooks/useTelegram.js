import { useEffect, useMemo, useState } from 'react'

function readLaunchData(tg) {
  var initData = (tg && tg.initData) || ''
  var sectorToken = new URLSearchParams(window.location.search || '').get('sectorLaunch') || ''
  var sectorUser = null
  if (sectorToken) {
    var uid = Number(sectorToken.split('.')[0])
    if (uid) { initData = 'sector:' + sectorToken; sectorUser = { id: uid, first_name: 'کاربر سکتور' } }
  }

  // Telegram iOS can expose the launch parameters in the URL a few frames
  // before telegram-web-app.js copies them onto WebApp.initData.
  if (!initData) {
    var hashParams = new URLSearchParams((window.location.hash || '').replace(/^#/, ''))
    var queryParams = new URLSearchParams(window.location.search || '')
    initData = hashParams.get('tgWebAppData') || queryParams.get('tgWebAppData') || ''
  }

  var user = sectorUser || (tg && tg.initDataUnsafe && tg.initDataUnsafe.user)
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
  var [photoUrl, setPhotoUrl] = useState('')
  var [telegram, setTelegram] = useState(function() {
    return readLaunchData(window.Telegram && window.Telegram.WebApp)
  })

  useEffect(function() {
    var cancelled = false
    var attempts = 0
    var timer
    var deadline = window.setTimeout(function() {
      if (!cancelled) setTelegram(function(current) { return { ...current, launchChecked: true } })
    }, 1800)

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

      attempts += 1
      var next = readLaunchData(tg)
      if (attempts === 1 || next.launchChecked) {
        try {
          fetch('https://telegram-group-manager-bot-iota.vercel.app/api/miniapp-diagnostic', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({bridge:Boolean(tg),user:Boolean(next.tgUser),init:Boolean(next.initData),version:(tg&&tg.version)||'',platform:(tg&&tg.platform)||'',phase:'launch'})})
        } catch (_) {}
      }
      next.launchChecked = Boolean(next.initData && next.tgUser) || attempts >= 18
      setTelegram(next)

      // Allow the native Telegram bridge time to hydrate on slower iOS opens.
      if ((!next.initData || !next.tgUser) && attempts < 18) {
        timer = window.setTimeout(syncTelegram, 100)
      }
    }

    syncTelegram()
    return function() {
      cancelled = true
      window.clearTimeout(timer)
      window.clearTimeout(deadline)
    }
  }, [])

  var resolvedUser = useMemo(function() {
    return telegram.tgUser ? { ...telegram.tgUser, photo_url: photoUrl || telegram.tgUser.photo_url } : null
  }, [telegram.tgUser, photoUrl])

  return { ...telegram, tgUser: resolvedUser, setPhotoUrl: setPhotoUrl }
}
