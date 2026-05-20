const API_URL = '/api/v1/admin'

function getAuthHeaders(token) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

async function adminRequest(path, token, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: getAuthHeaders(token),
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(data?.detail || `Ошибка ${response.status}`)
  }

  return data
}

export function getAdminUsers(token) {
  return adminRequest('/users', token)
}

export function updateAdminUserStatus(token, userId, payload) {
  return adminRequest(`/users/${userId}/status`, token, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getAdminListings(token) {
  return adminRequest('/listings', token)
}

export function archiveAdminListing(token, listingId) {
  return adminRequest(`/listings/${listingId}`, token, {
    method: 'DELETE',
  })
}

export function getAdminExchanges(token) {
  return adminRequest('/exchanges', token)
}

export function cancelAdminExchange(token, exchangeId) {
  return adminRequest(`/exchanges/${exchangeId}`, token, {
    method: 'DELETE',
  })
}

export function getAdminChats(token) {
  return adminRequest('/chats', token)
}

export function closeAdminChat(token, chatId) {
  return adminRequest(`/chats/${chatId}`, token, {
    method: 'DELETE',
  })
}

export function getAdminChatMessages(token, chatId) {
  return adminRequest(`/chats/${chatId}/messages`, token)
}
