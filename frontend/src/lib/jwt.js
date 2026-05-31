/**
 * Decode JWT payload (no signature verification — UI / header injection only).
 * Expects numeric user id in `sub`, `user_id`, or `id`.
 */
function base64UrlDecode(segment) {
  let b64 = segment.replace(/-/g, '+').replace(/_/g, '/')
  const pad = b64.length % 4
  if (pad) b64 += '='.repeat(4 - pad)
  const binary = atob(b64)
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

/**
 * @param {string | null | undefined} token
 * @returns {string | null}
 */
export function jwtUserRole(token) {
  if (!token || typeof token !== 'string') return null
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    const payload = JSON.parse(base64UrlDecode(parts[1]))
    return payload.role ?? null
  } catch {
    return null
  }
}

/**
 * @param {string | null | undefined} token
 * @returns {number | null}
 */
export function jwtUserId(token) {
  if (!token || typeof token !== 'string') return null
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    const json = base64UrlDecode(parts[1])
    const payload = JSON.parse(json)
    const raw = payload.sub ?? payload.user_id ?? payload.id
    if (raw == null) return null
    const n = Number(raw)
    return Number.isFinite(n) ? n : null
  } catch {
    return null
  }
}
