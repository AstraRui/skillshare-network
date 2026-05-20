import { jwtUserId } from '../lib/jwt.js'

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

function errorMessage(data, res) {
  if (typeof data !== 'object' || data == null) return res.statusText || `HTTP ${res.status}`
  const { detail } = data
  if (Array.isArray(detail)) return detail.map((d) => d.msg || d).join(', ')
  if (typeof detail === 'string') return detail
  return res.statusText || `HTTP ${res.status}`
}

export async function request(path, options = {}) {
  const { method = 'GET', body, skipAuth = false } = options
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (!skipAuth) {
    const token = localStorage.getItem('ssn_token')
    const id = token ? jwtUserId(token) : null
    if (id != null) headers['X-User-Id'] = String(id)
  }
  const res = await fetch(`${API_PREFIX}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  const data = await parseBody(res)
  if (!res.ok) throw new Error(errorMessage(data, res))
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

  // ── Exchanges ─────────────────────────────────────────────────────────────
  myExchanges: () => request('/exchanges'),
  acceptInterest: (listingId, responderId) =>
    request(`/exchanges/listing/${listingId}/accept-interest`, {
      method: 'POST',
      body: { responder_id: responderId },
    }),
  confirmExchangeCompletion: (exchangeId) =>
    request(`/exchanges/${exchangeId}/confirm-completion`, { method: 'POST' }),

  // ── Chat ──────────────────────────────────────────────────────────────────
  // Сообщения чата идут через /exchanges/{id}/messages (exchange_id, не chat_id)
  chatMessages: (exchangeId) => request(`/exchanges/${exchangeId}/messages`),
  sendChatMessage: (exchangeId, content) =>
    request(`/exchanges/${exchangeId}/messages`, { method: 'POST', body: { content } }),
  // Получить chat_id по exchange_id (нужен для WebSocket)
  getChatByExchange: (exchangeId) => request(`/chat/exchanges/${exchangeId}`),

  // ── Matches ───────────────────────────────────────────────────────────────
  matches: () => request('/matches'),
}
