import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import { api } from '../api/client.js'
import { jwtUserId, jwtUserRole } from '../lib/jwt.js'
import { initialsFromEmail } from '../lib/userDisplay.js'

const AuthContext = createContext(null)

const TOKEN_KEY = 'ssn_token'
const EMAIL_KEY = 'ssn_email'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [email, setEmail] = useState(() => localStorage.getItem(EMAIL_KEY))
  const [authModalOpen, setAuthModalOpen] = useState(false)
  // true сразу после регистрации — сигнал для редиректа на онбординг
  const [justRegistered, setJustRegistered] = useState(false)

  const openAuthModal = useCallback(() => setAuthModalOpen(true), [])
  const closeAuthModal = useCallback(() => setAuthModalOpen(false), [])
  const clearJustRegistered = useCallback(() => setJustRegistered(false), [])

  const userId = useMemo(() => (token ? jwtUserId(token) : null), [token])
  const isAdmin = useMemo(() => jwtUserRole(token) === 'admin', [token])

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
    await api.register({ email: regEmail, password, full_name: full_name || null })
    // Сразу логиним — не гоняем пользователя на форму входа
    await login(regEmail, password)
    setJustRegistered(true)
  }, [login])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(EMAIL_KEY)
    setToken(null)
    setEmail(null)
    setJustRegistered(false)
  }, [])

  const value = useMemo(
    () => ({
      token,
      userId,
      email,
      userInitials,
      isAuthenticated: Boolean(token && userId != null),
      isAdmin,
      justRegistered,
      clearJustRegistered,
      login,
      register,
      logout,
      authModalOpen,
      openAuthModal,
      closeAuthModal,
    }),
    [
      token,
      userId,
      isAdmin,
      email,
      userInitials,
      justRegistered,
      clearJustRegistered,
      login,
      register,
      logout,
      authModalOpen,
      openAuthModal,
      closeAuthModal,
    ],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components -- hook next to provider
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
