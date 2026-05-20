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
