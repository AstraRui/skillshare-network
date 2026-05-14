import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import { api } from '../api/client.js'
import { jwtUserId } from '../lib/jwt.js'
import { initialsFromEmail } from '../lib/userDisplay.js'

const AuthContext = createContext(null)

const TOKEN_KEY = 'ssn_token'
const EMAIL_KEY = 'ssn_email'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [email, setEmail] = useState(() => localStorage.getItem(EMAIL_KEY))

  const userId = useMemo(() => (token ? jwtUserId(token) : null), [token])

  const userInitials = useMemo(() => {
    if (!email) return '?'
    return initialsFromEmail(email)
  }, [email])

  const login = useCallback(async (loginEmail, password) => {
    const { access_token: accessToken } = await api.login(loginEmail, password)
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(EMAIL_KEY, loginEmail)
    setToken(accessToken)
    setEmail(loginEmail)
  }, [])

  const register = useCallback(async ({ email: regEmail, password, full_name }) => {
    return api.register({ email: regEmail, password, full_name: full_name || null })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(EMAIL_KEY)
    setToken(null)
    setEmail(null)
  }, [])

  const value = useMemo(
    () => ({
      token,
      userId,
      email,
      userInitials,
      isAuthenticated: Boolean(token && userId != null),
      login,
      register,
      logout,
    }),
    [token, userId, email, userInitials, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components -- hook next to provider
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
