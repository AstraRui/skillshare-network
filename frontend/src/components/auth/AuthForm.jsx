import { useState } from 'react'
import { useAuth } from '../../context/AuthContext.jsx'

function AuthForm({ onAuthenticated, className = '' }) {
  const { login, register } = useAuth()
  const [loginEmail, setLoginEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [mode, setMode] = useState('login')
  const [formError, setFormError] = useState(null)
  const [formOk, setFormOk] = useState(null)

  const switchMode = (next) => {
    setMode(next)
    setFormError(null)
    setFormOk(null)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setFormError(null)
    setFormOk(null)
    try {
      await login(loginEmail.trim(), password)
      setPassword('')
      onAuthenticated?.()
    } catch (err) {
      setFormError(err.message || 'Ошибка входа')
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setFormError(null)
    setFormOk(null)
    try {
      await register({
        email: loginEmail.trim(),
        password,
        full_name: fullName.trim() || undefined,
      })
      setFormOk('Аккаунт создан. Теперь войдите.')
      setMode('login')
      setPassword('')
    } catch (err) {
      setFormError(err.message || 'Ошибка регистрации')
    }
  }

  return (
    <form
      className={`space-y-3 text-left ${className}`}
      onSubmit={mode === 'login' ? handleLogin : handleRegister}
    >
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => switchMode('login')}
          className={`flex-1 rounded-lg py-2 text-[10px] font-black uppercase ${
            mode === 'login' ? 'bg-indigo-600 text-white' : 'bg-white/5 text-slate-400'
          }`}
        >
          Вход
        </button>
        <button
          type="button"
          onClick={() => switchMode('register')}
          className={`flex-1 rounded-lg py-2 text-[10px] font-black uppercase ${
            mode === 'register' ? 'bg-indigo-600 text-white' : 'bg-white/5 text-slate-400'
          }`}
        >
          Регистрация
        </button>
      </div>
      {mode === 'register' ? (
        <input
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Имя (необязательно)"
          className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
        />
      ) : null}
      <input
        type="email"
        required
        autoComplete="email"
        value={loginEmail}
        onChange={(e) => setLoginEmail(e.target.value)}
        placeholder="Email"
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
      />
      <input
        type="password"
        required
        minLength={10}
        autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Пароль (≥10 символов)"
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
      />
      {formError ? <p className="text-xs text-red-400">{formError}</p> : null}
      {formOk ? <p className="text-xs text-green-400">{formOk}</p> : null}
      <button
        type="submit"
        className="w-full rounded-xl bg-indigo-600 py-3 text-xs font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
      >
        {mode === 'login' ? 'Войти' : 'Создать аккаунт'}
      </button>
    </form>
  )
}

export default AuthForm
