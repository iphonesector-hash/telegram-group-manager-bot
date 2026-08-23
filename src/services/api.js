const BASE = import.meta.env.VITE_API_BASE_URL || 'https://telegram-group-manager-bot-iota.vercel.app'

async function request(endpoint, options, initData) {
  try {
    const res = await fetch(BASE + endpoint, {...options, headers: {'Content-Type': 'application/json','init-data': initData || '',...(options && options.headers)}})
    const payload = await res.json().catch(function() { return null })
    if (!res.ok) throw new Error((payload && payload.detail) || ('HTTP ' + res.status))
    return { data: payload, error: null }
  } catch (err) { console.warn('[API]', endpoint, err.message); return { data: null, error: err.message } }
}

export const api = {
  getMembership: function(userId, initData) { return request('/api/membership/' + userId, {}, initData) },
  getUser: function(userId, initData) { return request('/api/user/' + userId, {}, initData) },
  getUserPhoto: function(userId, initData) { return request('/api/user-photo/' + userId, {}, initData) },
  dailyClaim: function(userId, initData) { return request('/api/daily-claim/' + userId, { method: 'POST' }, initData) },
  spinWheel: function(userId, initData) { return request('/api/wheel/spin/' + userId, { method: 'POST' }, initData) },
  getWheelHistory: function(userId, initData) { return request('/api/wheel/history/' + userId, {}, initData) },
  getShop: function(initData) { return request('/api/shop', {}, initData) },
  buyItem: function(userId, itemId, couponCode, initData) { return request('/api/shop/buy/' + userId + '?item_id=' + itemId + '&coupon_code=' + encodeURIComponent(couponCode || ''), { method: 'POST' }, initData) },
  getLeaderboard: function(initData) { return request('/api/leaderboard', {}, initData) },
  getOrders: function(userId, initData) { return request('/api/orders/' + userId, {}, initData) },
  renewOrder: function(userId, orderId, initData) { return request('/api/orders/' + userId + '/' + orderId + '/renew', { method:'POST' }, initData) },
  getTransactions: function(userId, initData) { return request('/api/transactions/' + userId, {}, initData) },
  getGames: function(initData) { return request('/api/games', {}, initData) },
  createGameSession: function(userId, gameKey, initData) { return request('/api/games/session/' + userId + '/' + encodeURIComponent(gameKey), { method:'POST', body:'{}' }, initData) },
  submitGameScore: function(userId, payload, initData) { return request('/api/games/score/' + userId, { method:'POST', body:JSON.stringify(payload) }, initData) },
  getGameLeaderboard: function(gameKey, initData) { return request('/api/games/leaderboard/' + encodeURIComponent(gameKey), {}, initData) },
  getGroups: function(userId, initData) { return request('/api/groups/' + userId, {}, initData) },
  getBank: function(userId, initData) { return request('/api/bank/' + userId, {}, initData) },
  bankAction: function(userId, action, amount, initData) { return request('/api/bank/' + userId + '/' + action + '?amount=' + Number(amount || 0), { method: 'POST' }, initData) },
  getQuiz: function(kind, initData) { return request('/api/quiz?kind=' + encodeURIComponent(kind || 'intel'), {}, initData) },
  answerQuiz: function(userId, questionId, choice, initData) { return request('/api/quiz/answer/' + userId + '?question_id=' + encodeURIComponent(questionId) + '&choice=' + Number(choice), { method: 'POST' }, initData) },
  getAdminOverview: function(initData) { return request('/api/admin/overview', {}, initData) },
  updateAdminSettings: function(settings, initData) { return request('/api/admin/settings', { method:'POST', body:JSON.stringify({ settings:settings }) }, initData) },
  assistant: function(userId, message, mode, history, initData) { return request('/api/tools/assistant/' + userId, { method:'POST', body:JSON.stringify({ message:message, mode:mode, history:history || [] }) }, initData) },
  weather: function(city, initData) { return request('/api/tools/weather?city=' + encodeURIComponent(city), {}, initData) },
  calculate: function(expression, initData) { return request('/api/tools/calculate', { method:'POST', body:JSON.stringify({ expression:expression }) }, initData) },
  getMissions: function(userId, initData) { return request('/api/missions/' + userId, {}, initData) },
  claimMission: function(userId, missionId, initData) { return request('/api/missions/' + userId + '/' + encodeURIComponent(missionId) + '/claim', { method:'POST' }, initData) },

  getSectorPet: function(userId, initData) { return request('/api/sector-v2/' + userId, {}, initData) },
  sectorPetAction: function(userId, action, initData) { return request('/api/sector-v2/' + userId + '/action/' + encodeURIComponent(action), { method:'POST' }, initData) },
  talkSectorPet: function(userId, message, initData) { return request('/api/sector-v2/' + userId + '/talk', { method:'POST', body:JSON.stringify({message:message}) }, initData) },
  buySectorShopItem: function(userId, itemKey, initData) { return request('/api/sector-v2/' + userId + '/shop/' + encodeURIComponent(itemKey) + '/buy', { method:'POST', body:'{}' }, initData) },
  equipSectorShopItem: function(userId, itemKey, initData) { return request('/api/sector-v2/' + userId + '/shop/' + encodeURIComponent(itemKey) + '/equip', { method:'POST', body:'{}' }, initData) },
  unequipSectorSlot: function(userId, slot, initData) { return request('/api/sector-v2/' + userId + '/shop/slot/' + encodeURIComponent(slot) + '/unequip', { method:'POST', body:'{}' }, initData) },
  renameSectorPet: function(userId, name, initData) { return request('/api/sector-v2/' + userId + '/rename', { method:'POST', body:JSON.stringify({name:name}) }, initData) },
  finishSectorGame: function(userId, gameKey, score, initData) { return request('/api/sector-v2/' + userId + '/minigame/' + encodeURIComponent(gameKey), { method:'POST', body:JSON.stringify({score:score}) }, initData) },
  sectorSocial: function(userId, action, target, initData) { return request('/api/sector-v2/' + userId + '/social/' + encodeURIComponent(action), { method:'POST', body:JSON.stringify({target:target}) }, initData) },
  getSectorLeaderboard: function(initData) { return request('/api/sector-v2-leaderboard', {}, initData) },
  getSectorMeta: function(userId, initData) { return request('/api/sector-meta/' + userId, {}, initData) },
  claimSectorReward: function(userId, kind, key, initData) { return request('/api/sector-meta/' + userId + '/claim/' + encodeURIComponent(kind) + '/' + encodeURIComponent(key), { method:'POST', body:'{}' }, initData) },
  attackSectorBoss: function(userId, initData) { return request('/api/sector-meta/' + userId + '/boss/attack', { method:'POST', body:'{}' }, initData) },
  advanceSectorStoryV2: function(userId, initData) { return request('/api/sector-meta/' + userId + '/story/advance', { method:'POST', body:'{}' }, initData) },
  getSectorSeasonLeaderboard: function(initData) { return request('/api/sector-season-leaderboard', {}, initData) },
  getSectorLedger: function(userId, initData) { return request('/api/sector-meta/' + userId + '/ledger', {}, initData) },
  sellSectorShopItem: function(userId, itemKey, initData) { return request('/api/sector-meta/' + userId + '/shop/' + encodeURIComponent(itemKey) + '/sell', { method:'POST', body:'{}' }, initData) },
  chooseSectorEvolutionV2: function(userId, pathKey, initData) { return request('/api/sector-meta/' + userId + '/evolution/' + encodeURIComponent(pathKey), { method:'POST', body:'{}' }, initData) },
  claimPreviousSectorSeason: function(userId, initData) { return request('/api/sector-meta/' + userId + '/season/claim-previous', { method:'POST', body:'{}' }, initData) },
  getSectorMetaAnalytics: function(userId, initData) { return request('/api/sector-meta-admin/' + userId + '/analytics', {}, initData) },

  buySectorRoomItem: function(userId, itemKey, initData) { return request('/api/sector-pet/' + userId + '/room/' + encodeURIComponent(itemKey), { method:'POST', body:'{}' }, initData) },
  chooseSectorEvolution: function(userId, pathKey, initData) { return request('/api/sector-pet/' + userId + '/evolution/' + encodeURIComponent(pathKey), { method:'POST', body:'{}' }, initData) },
  buySectorCosmetic: function(userId, itemKey, initData) { return request('/api/sector-pet/' + userId + '/cosmetic/' + encodeURIComponent(itemKey), { method:'POST', body:'{}' }, initData) },
  advanceSectorStory: function(userId, initData) { return request('/api/sector-pet/' + userId + '/story/advance', { method:'POST', body:'{}' }, initData) },
  sectorJob: function(userId, jobKey, initData) { return request('/api/sector-pet/' + userId + '/job/' + encodeURIComponent(jobKey), { method:'POST', body:'{}' }, initData) },
  getSectorAdmin: function(userId, initData) { return request('/api/sector-admin/' + userId, {}, initData) },
  updateSectorAdmin: function(userId, data, initData) { return request('/api/sector-admin/' + userId, { method:'POST', body:JSON.stringify(data) }, initData) },
  setSectorNotifications: function(userId, enabled, initData) { return request('/api/sector-pet/' + userId + '/notifications/' + (enabled?1:0), { method:'POST', body:'{}' }, initData) },
  sectorClan: function(userId, action, name, initData) { return request('/api/sector-clan/' + userId + '/' + encodeURIComponent(action), { method:'POST', body:JSON.stringify({name:name}) }, initData) },
  sendSectorGift: function(userId, amount, initData) { return request('/api/sector-admin/' + userId + '/gift', { method:'POST', body:JSON.stringify({amount:amount}) }, initData) },
}
