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
  if (res.status === 204) return null
  return data
}

export const api = {
  health: () => request('/health'),
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: { email, password },
      skipAuth: true,
    }),
  register: (payload) =>
    request('/auth/register', { method: 'POST', body: payload, skipAuth: true }),
  user: (userId) => request(`/users/${userId}`, { skipAuth: true }),
  myProfile: () => request('/users/me'),
  updateMyProfile: (payload) => request('/users/me', { method: 'PATCH', body: payload }),
  mySkills: () => request('/users/me/skills'),
  addOfferedSkill: (payload) =>
    request('/users/me/skills/offered', { method: 'POST', body: payload }),
  addWantedSkill: (payload) =>
    request('/users/me/skills/wanted', { method: 'POST', body: payload }),
  removeOfferedSkill: (skillId) =>
    request(`/users/me/skills/offered/${skillId}`, { method: 'DELETE' }),
  removeWantedSkill: (skillId) =>
    request(`/users/me/skills/wanted/${skillId}`, { method: 'DELETE' }),
  myExchanges: () => request('/exchanges'),
  updateExchangeStatus: (exchangeId, to) =>
    request(`/exchanges/${exchangeId}/status`, { method: 'POST', body: { to } }),
  exchangeMessages: (exchangeId) => request(`/exchanges/${exchangeId}/messages`),
  postExchangeMessage: (exchangeId, content) =>
    request(`/exchanges/${exchangeId}/messages`, {
      method: 'POST',
      body: { content },
    }),
  confirmExchangeCompletion: (exchangeId) =>
    request(`/exchanges/${exchangeId}/confirm-completion`, { method: 'POST' }),
  myExchangeReview: (exchangeId) => request(`/exchanges/${exchangeId}/reviews/mine`),
  submitExchangeReview: (exchangeId, payload) =>
    request(`/exchanges/${exchangeId}/reviews`, { method: 'POST', body: payload }),
  listings: (params = {}) => {
    const q = new URLSearchParams()
    for (const [k, v] of Object.entries(params)) {
      if (v != null && v !== '') q.set(k, String(v))
    }
    const s = q.toString()
    return request(s ? `/listings?${s}` : '/listings', { skipAuth: true })
  },
  createListing: (payload) => request('/listings', { method: 'POST', body: payload }),
  updateListing: (listingId, payload) =>
    request(`/listings/${listingId}`, { method: 'PATCH', body: payload }),
  createListingInterest: (listingId, payload = {}) =>
    request(`/listings/${listingId}/interests`, { method: 'POST', body: payload }),
  incomingInterests: () => request('/listings/me/incoming-interests'),
  listingInterests: (listingId) => request(`/listings/${listingId}/interests`),
  acceptListingInterest: (listingId, responderId) =>
    request(`/exchanges/listing/${listingId}/accept-interest`, {
      method: 'POST',
      body: { responder_id: responderId },
    }),
  matches: () => request('/matches'),
}
