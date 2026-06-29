import { useState, useRef, useCallback } from 'react'

export function useToast() {
  const [toast, setToast] = useState({ msg: '', show: false, type: 'info' })
  const timer = useRef(null)

  const showToast = useCallback(function(msg, type) {
    if (timer.current) clearTimeout(timer.current)
    setToast({ msg: msg, show: true, type: type || 'info' })
    timer.current = setTimeout(function() {
      setToast(function(t) { return { ...t, show: false } })
    }, 2800)
  }, [])

  return { toast: toast, showToast: showToast }
}
