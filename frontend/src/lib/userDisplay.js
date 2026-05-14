

/**
 * @param {string | null | undefined} email
 * @returns {string} 1–2 символа, латиница/кириллица
 */
export function initialsFromEmail(email) {
  if (!email || typeof email !== 'string') return '?'
  const local = email.split('@')[0]?.trim() || ''
  if (!local) return '?'
  const parts = local.replace(/[._-]+/g, ' ').split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    const a = parts[0][0] ?? ''
    const b = parts[1][0] ?? ''
    return (a + b).toUpperCase().slice(0, 2)
  }
  return local.slice(0, 2).toUpperCase()
}

/**
 * @param {string | null | undefined} email
 * @param {number} max
 */
export function truncateEmail(email, max = 22) {
  if (!email) return ''
  return email.length <= max ? email : `${email.slice(0, max - 1)}…`
}
