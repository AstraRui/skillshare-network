const API_PREFIX = '/api/v1'

async function parseBody(res) {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

const STATUS_FALLBACKS = {
  401: 'Неверный email или пароль',
  409: 'Этот email уже зарегистрирован',
  422: 'Проверьте введённые данные',
  500: 'Ошибка сервера. Попробуйте позже',
}

function validationEntryMessage(entry) {
  if (typeof entry === 'string') return entry
  const msg = entry?.msg
  if (typeof msg !== 'string') return ''
  return msg.startsWith('Value error, ') ? msg.slice('Value error, '.length) : msg
}

function errorMessage(data, res) {
  if (typeof data === 'object' && data != null) {
    const { detail } = data
    if (typeof detail === 'string' && detail.trim()) return detail
    if (Array.isArray(detail)) {
      const text = detail.map(validationEntryMessage).filter(Boolean).join('. ')
      if (text) return text
    }
  }
  return STATUS_FALLBACKS[res.status] || res.statusText || `Ошибка ${res.status}`
}

export async function request(path, options = {}) {
  const { method = 'GET', body, skipAuth = false } = options
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (!skipAuth) {
    const token = localStorage.getItem('ssn_token')
    if (token && token !== 'null' && token !== 'undefined') {
      headers['Authorization'] = `Bearer ${token}`
    }
  }
  const res = await fetch(`${API_PREFIX}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  const data = await parseBody(res)
  if (res.status === 401) {
    // Токен невалиден или истек - очищаем и перезагружаем
    localStorage.removeItem('ssn_token')
    localStorage.removeItem('ssn_email')
    window.location.reload()
    return null
  }
  if (!res.ok) throw new Error(errorMessage(data, res))
  if (res.status === 204) return null
  return data
}

export const api = {
  health: () => request('/health'),

  // ── Auth ──────────────────────────────────────────────────────────────────
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: { email, password },
      skipAuth: true,
    }),
  register: (payload) =>
    request('/auth/register', { method: 'POST', body: payload, skipAuth: true }),

  // ── Users ─────────────────────────────────────────────────────────────────
  getMe: () => request('/users/me'),
  updateMe: (payload) => request('/users/me', { method: 'PATCH', body: payload }),
  updateMyProfile: (payload) => request('/users/me', { method: 'PATCH', body: payload }),
  changePassword: (current_password, new_password) =>
    request('/users/me/password', { method: 'PATCH', body: { current_password, new_password } }),
  getMySkills: () => request('/users/me/skills'),
  updateMySkills: (payload) => request('/users/me/skills', { method: 'PUT', body: payload }),

  // ── Skills ────────────────────────────────────────────────────────────────
  skills: () => request('/skills'),
  skillCategories: () => request('/skills/categories'),
  createSkill: (name) => request('/skills', { method: 'POST', body: { name } }),

  // ── Listings ──────────────────────────────────────────────────────────────
  listings: (params = {}) => {
    const q = new URLSearchParams()
    for (const [k, v] of Object.entries(params)) {
      if (v != null && v !== '') q.set(k, String(v))
    }
    const s = q.toString()
    return request(s ? `/listings?${s}` : '/listings')
  },
  createListing: (payload) => request('/listings', { method: 'POST', body: payload }),
  respondToListing: (listingId, message = null) =>
    request(`/listings/${listingId}/interests`, { method: 'POST', body: { message } }),
  listingInterests: (listingId) => request(`/listings/${listingId}/interests`),
  incomingInterests: () => request('/listings/me/incoming-interests'),
  updateListing: (listingId, payload) =>
    request(`/listings/${listingId}`, { method: 'PATCH', body: payload }),
  createListingInterest: (listingId, payload = {}) =>
    request(`/listings/${listingId}/interests`, { method: 'POST', body: payload }),
  acceptListingInterest: (listingId, responderId) =>
    request(`/exchanges/listing/${listingId}/accept-interest`, {
      method: 'POST',
      body: { responder_id: responderId },
    }),

  // ── Exchanges ─────────────────────────────────────────────────────────────
  myExchanges: () => request('/exchanges'),
  startDirectExchange: (targetUserId) =>
    request('/exchanges/direct', { method: 'POST', body: { target_user_id: targetUserId } }),
  acceptInterest: (listingId, responderId) =>
    request(`/exchanges/listing/${listingId}/accept-interest`, {
      method: 'POST',
      body: { responder_id: responderId },
    }),
  updateExchangeStatus: (exchangeId, to) =>
    request(`/exchanges/${exchangeId}/status`, { method: 'POST', body: { to } }),
  requestStartExchange: (exchangeId) =>
    request(`/exchanges/${exchangeId}/request-start`, { method: 'POST' }),
  confirmExchangeCompletion: (exchangeId) =>
    request(`/exchanges/${exchangeId}/confirm-completion`, { method: 'POST' }),

  exchangeReviews: (exchangeId) => request(`/exchanges/${exchangeId}/reviews`),
  submitReview: (exchangeId, rating, comment) =>
    request(`/exchanges/${exchangeId}/reviews`, {
      method: 'POST',
      body: { rating, comment: comment || null },
    }),
  myReceivedReviews: () => request('/users/me/reviews'),

  // ── Chat ──────────────────────────────────────────────────────────────────
  // Сообщения чата идут через /exchanges/{id}/messages (exchange_id, не chat_id)
  chatMessages: (exchangeId) => request(`/exchanges/${exchangeId}/messages`),
  sendChatMessage: (exchangeId, content) =>
    request(`/exchanges/${exchangeId}/messages`, { method: 'POST', body: { content } }),
  // Получить chat_id по exchange_id (нужен для WebSocket)
  getChatByExchange: (exchangeId) => request(`/chat/exchanges/${exchangeId}`),

  // ── Matches ───────────────────────────────────────────────────────────────
  matches: () => request('/matches'),

  // ── Admin ─────────────────────────────────────────────────────────────────
  adminExchanges: (params = {}) => {
    const q = new URLSearchParams()
    for (const [k, v] of Object.entries(params)) {
      if (v != null && v !== '') q.set(k, String(v))
    }
    const s = q.toString()
    return request(s ? `/admin/exchanges?${s}` : '/admin/exchanges')
  },
}
