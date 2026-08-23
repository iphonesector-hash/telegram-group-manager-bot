// The Mini App is deployed as a separate static Vercel project.  Its own
// /api runtime intentionally has no bot/database secrets, so authenticated
// requests must always go to the unified bot backend.
const BASE = import.meta.env.VITE_API_BASE_URL || 'https://telegram-group-manager-bot-iota.vercel.app'

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
    const payload = await res.json().catch(function() { return null })
    if (!res.ok) throw new Error((payload && payload.detail) || ('HTTP ' + res.status))
    return { data: payload, error: null }
  } catch (err) {
    console.warn('[API]', endpoint, err.message)
    return { data: null, error: err.message }
  }
}

export const api = {
  getUser: function(userId, initData) { return request('/api/user/' + userId, {}, initData) },
  getUserPhoto: function(userId, initData) { return request('/api/user-photo/' + userId, {}, initData) },
  dailyClaim: function(userId, initData) { return request('/api/daily-claim/' + userId, { method: 'POST' }, initData) },
  spinWheel: function(userId, initData) { return request('/api/wheel/spin/' + userId, { method: 'POST' }, initData) },
  getShop: function(initData) { return request('/api/shop', {}, initData) },
  buyItem: function(userId, itemId, initData) { return request('/api/shop/buy/' + userId + '?item_id=' + itemId, { method: 'POST' }, initData) },
  getLeaderboard: function(initData) { return request('/api/leaderboard', {}, initData) },
  getOrders: function(userId, initData) { return request('/api/orders/' + userId, {}, initData) },
  getTransactions: function(userId, initData) { return request('/api/transactions/' + userId, {}, initData) },
  getGames: function(initData) { return request('/api/games', {}, initData) },
  getGroups: function(userId, initData) { return request('/api/groups/' + userId, {}, initData) },
  getBank: function(userId, initData) { return request('/api/bank/' + userId, {}, initData) },
  bankAction: function(userId, action, amount, initData) {
    return request('/api/bank/' + userId + '/' + action + '?amount=' + Number(amount || 0), { method: 'POST' }, initData)
  },
  getQuiz: function(kind, initData) { return request('/api/quiz?kind=' + encodeURIComponent(kind || 'intel'), {}, initData) },
  answerQuiz: function(userId, questionId, choice, initData) {
    return request('/api/quiz/answer/' + userId + '?question_id=' + encodeURIComponent(questionId) + '&choice=' + Number(choice), { method: 'POST' }, initData)
  },
  getAdminOverview: function(initData) { return request('/api/admin/overview', {}, initData) },
  updateAdminSettings: function(settings, initData) { return request('/api/admin/settings', { method:'POST', body:JSON.stringify({ settings:settings }) }, initData) },
}
