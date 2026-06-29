const BASE = import.meta.env.VITE_API_BASE_URL || ''

async function request(endpoint, options, initData) {
  try {
    const res = await fetch(BASE + endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'init-data': initData || '',
        ...(options && options.headers),
      },
    })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    return { data: await res.json(), error: null }
  } catch (err) {
    console.warn('[API]', endpoint, err.message)
    return { data: null, error: err.message }
  }
}

export const api = {
  getUser:       function(userId, initData)         { return request('/api/user/' + userId, {}, initData) },
  dailyClaim:    function(userId, initData)         { return request('/api/daily-claim/' + userId, { method: 'POST' }, initData) },
  getShop:       function(initData)                 { return request('/api/shop', {}, initData) },
  buyItem:       function(userId, itemId, initData) { return request('/api/shop/buy/' + userId + '?item_id=' + itemId, { method: 'POST' }, initData) },
  getLeaderboard:function(initData)                 { return request('/api/leaderboard', {}, initData) },
  getOrders:     function(userId, initData)         { return request('/api/orders/' + userId, {}, initData) },
}
