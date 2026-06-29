import { useState, useCallback } from 'react'
import { api } from '../services/api'

export function useApi(initData) {
  const [loading, setLoading] = useState(false)

  const call = useCallback(function(apiFn) {
    setLoading(true)
    return apiFn(initData).finally(function() { setLoading(false) })
  }, [initData])

  return { call: call, loading: loading }
}
