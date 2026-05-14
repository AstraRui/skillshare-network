import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Award,
  Bell,
  CheckCircle2,
  LogOut,
  PlusCircle,
  Settings,
  Share2,
  ShieldCheck,
  X,
  Zap,
} from 'lucide-react'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

const userProfile = {
  name: 'Алексей Иванов',
  reputation: 4.92,
  skills: ['UI/UX Design', 'Figma', 'React Basics', 'Prototyping'],
  needs: ['Python Development', 'Legal Audit', 'SEO Marketing'],
}

function ProfilePage() {
  const location = useLocation()
  const { isAuthenticated, userId, email, login, register, logout } = useAuth()
  const [loginEmail, setLoginEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [mode, setMode] = useState('login')
  const [formError, setFormError] = useState(null)
  const [formOk, setFormOk] = useState(null)
  const [myListings, setMyListings] = useState([])

  useEffect(() => {
    if (!isAuthenticated || !userId) return
    let c = false
    queueMicrotask(() => {
      void (async () => {
        try {
          const list = await api.listings({ author_id: userId })
          if (!c) setMyListings(list)
        } catch {
          if (!c) setMyListings([])
        }
      })()
    })
    return () => {
      c = true
    }
  }, [isAuthenticated, userId])

  const handleLogin = async (e) => {
    e.preventDefault()
    setFormError(null)
    setFormOk(null)
    try {
      await login(loginEmail.trim(), password)
      setFormOk('Вход выполнен')
      setPassword('')
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
    <div className="animate-page grid grid-cols-1 gap-8 lg:grid-cols-4">
      {typeof location.state?.from === 'string' && location.state.from ? (
        <div className="lg:col-span-4">
          <p className="rounded-2xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
            Для доступа к{' '}
            <span className="font-mono text-amber-50">{location.state.from}</span> войдите в аккаунт
            или зарегистрируйтесь.
          </p>
        </div>
      ) : null}
      <div className="space-y-6 lg:col-span-1">
        <div className="rounded-[40px] border border-white/5 bg-slate-900 p-6 text-center">
          <h3 className="mb-4 text-left text-sm font-black uppercase tracking-widest text-white">
            Аккаунт
          </h3>
          {isAuthenticated ? (
            <div className="space-y-3 text-left text-sm text-slate-300">
              <p>
                <span className="text-slate-500">Сессия:</span> {email}
              </p>
              <button
                type="button"
                onClick={() => {
                  logout()
                  setFormOk(null)
                }}
                className="w-full rounded-xl border border-white/10 bg-white/5 py-2 text-xs font-bold text-white transition hover:bg-white/10"
              >
                Выйти из аккаунта
              </button>
            </div>
          ) : (
            <form
              className="space-y-3 text-left"
              onSubmit={mode === 'login' ? handleLogin : handleRegister}
            >
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setMode('login')}
                  className={`flex-1 rounded-lg py-2 text-[10px] font-black uppercase ${
                    mode === 'login' ? 'bg-indigo-600 text-white' : 'bg-white/5 text-slate-400'
                  }`}
                >
                  Вход
                </button>
                <button
                  type="button"
                  onClick={() => setMode('register')}
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
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white outline-none"
                />
              ) : null}
              <input
                type="email"
                required
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder="Email"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white outline-none"
              />
              <input
                type="password"
                required
                minLength={10}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Пароль (≥10 символов)"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white outline-none"
              />
              {formError ? <p className="text-xs text-red-400">{formError}</p> : null}
              {formOk ? <p className="text-xs text-green-400">{formOk}</p> : null}
              <button
                type="submit"
                className="w-full rounded-xl bg-indigo-600 py-2.5 text-xs font-black uppercase tracking-widest text-white hover:bg-indigo-500"
              >
                {mode === 'login' ? 'Войти' : 'Создать аккаунт'}
              </button>
              <p className="text-[10px] leading-relaxed text-slate-500">
                Бэкенд ожидает заголовок <code className="text-indigo-300">X-User-Id</code> — он
                выставляется автоматически после входа (id из JWT).
              </p>
            </form>
          )}
        </div>

        <div className="group relative overflow-hidden rounded-[40px] border border-white/5 bg-slate-900 p-8 text-center">
          <div className="absolute left-0 top-0 h-1 w-full bg-gradient-to-r from-indigo-500 to-fuchsia-500" />
          <div className="mx-auto mb-6 flex size-24 rotate-3 items-center justify-center rounded-[32px] bg-indigo-600 text-3xl font-black text-white shadow-2xl transition-transform group-hover:rotate-0">
            АИ
          </div>
          <h3 className="text-xl font-black italic text-white">{userProfile.name}</h3>
          <p className="mt-1 text-xs font-bold uppercase tracking-widest text-slate-500">
            Moscow, Russia
          </p>
          <div className="mt-8 space-y-4 border-t border-white/5 pt-8">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-400">Репутация</span>
              <span className="font-black text-indigo-400">4.92 ★</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-400">Сделок</span>
              <span className="font-black text-white">24</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-400">Уровень</span>
              <span className="font-black uppercase text-fuchsia-400">PRO</span>
            </div>
          </div>
          <button
            type="button"
            className="mt-8 w-full rounded-2xl border border-white/10 bg-white/5 py-3 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-white/10"
          >
            Редактировать
          </button>
        </div>

        <div className="space-y-2 rounded-[32px] border border-white/5 bg-slate-900 p-6">
          <button
            type="button"
            className="flex w-full items-center space-x-3 rounded-xl border border-indigo-500/20 bg-indigo-600/10 p-3 text-indigo-400"
          >
            <Settings size={16} /> <span className="text-xs font-bold">Настройки аккаунта</span>
          </button>
          <button
            type="button"
            className="flex w-full items-center space-x-3 rounded-xl p-3 text-slate-400 transition hover:bg-white/5"
          >
            <ShieldCheck size={16} /> <span className="text-xs font-bold">Безопасность</span>
          </button>
          <button
            type="button"
            className="flex w-full items-center space-x-3 rounded-xl p-3 text-slate-400 transition hover:bg-white/5"
          >
            <Bell size={16} /> <span className="text-xs font-bold">Уведомления</span>
          </button>
          <button
            type="button"
            onClick={logout}
            className="mt-4 flex w-full items-center space-x-3 rounded-xl p-3 text-red-500 transition hover:bg-red-500/10"
          >
            <LogOut size={16} /> <span className="text-xs font-bold">Выйти</span>
          </button>
        </div>
      </div>

      <div className="space-y-8 lg:col-span-3">
        <div className="rounded-[40px] border border-white/5 bg-slate-900 p-8">
          <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h3 className="text-2xl font-black uppercase italic text-white">Skill Configuration</h3>
              <p className="mt-2 text-xs font-medium text-slate-500">
                Обновите свои навыки, чтобы алгоритм предложил лучшие цепочки.
              </p>
            </div>
            <button
              type="button"
              className="rounded-xl bg-indigo-500 p-2 text-white transition hover:bg-indigo-400"
              aria-label="Добавить"
            >
              <PlusCircle size={20} />
            </button>
          </div>

          {isAuthenticated && myListings.length > 0 ? (
            <div className="mb-8 rounded-2xl border border-white/10 bg-white/5 p-4 text-left">
              <h4 className="mb-2 text-[10px] font-black uppercase tracking-widest text-slate-400">
                Мои объявления (API)
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {myListings.map((l) => (
                  <li key={l.id}>
                    <span className="font-bold text-white">{l.title}</span> — {l.offering_summary}{' '}
                    / ищет: {l.seeking_summary}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            <div className="space-y-4">
              <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400">
                Я предлагаю
              </h4>
              <div className="flex flex-wrap gap-2">
                {userProfile.skills.map((s) => (
                  <span
                    key={s}
                    className="flex items-center space-x-2 rounded-xl border border-indigo-500/20 bg-indigo-500/10 px-4 py-2 text-xs font-bold text-white"
                  >
                    <span>{s}</span>
                    <X size={12} className="cursor-pointer text-slate-500 hover:text-white" />
                  </span>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-fuchsia-400">
                Я ищу (Needs)
              </h4>
              <div className="flex flex-wrap gap-2">
                {userProfile.needs.map((n) => (
                  <span
                    key={n}
                    className="flex items-center space-x-2 rounded-xl border border-fuchsia-500/20 bg-fuchsia-500/10 px-4 py-2 text-xs font-bold text-white"
                  >
                    <span>{n}</span>
                    <X size={12} className="cursor-pointer text-slate-500 hover:text-white" />
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
          <div className="rounded-[40px] border border-white/5 bg-slate-900 p-8">
            <h3 className="mb-6 text-lg font-black uppercase italic text-white">Trust Factors</h3>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-lg bg-green-500/10 p-2 text-green-400">
                    <CheckCircle2 size={16} />
                  </div>
                  <span className="text-sm font-bold text-slate-300">Identity Verified</span>
                </div>
                <span className="text-[10px] font-black text-green-500">CONFIRMED</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-400">
                    <Award size={16} />
                  </div>
                  <span className="text-sm font-bold text-slate-300">Expertise Score</span>
                </div>
                <span className="text-[10px] font-black text-white">98 / 100</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-lg bg-amber-500/10 p-2 text-amber-400">
                    <Zap size={16} />
                  </div>
                  <span className="text-sm font-bold text-slate-300">Response Speed</span>
                </div>
                <span className="text-[10px] font-black text-white">4.5h AVG</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col justify-between rounded-[40px] border border-white/10 bg-gradient-to-br from-indigo-900/40 to-fuchsia-900/40 p-8">
            <div>
              <h3 className="mb-4 text-left text-xl font-black uppercase italic leading-tight text-white">
                Infrastructure <br /> API Access
              </h3>
              <p className="text-left text-xs text-slate-400">
                Используйте ваш токен для интеграции SkillShare во внешние сервисы.
              </p>
            </div>
            <div className="mt-6 flex items-center space-x-2 rounded-2xl border border-white/5 bg-black/40 p-3">
              <code className="truncate font-mono text-[10px] text-indigo-300">
                sk_live_51M...889xx
              </code>
              <button type="button" className="p-1 text-slate-500 transition hover:text-white">
                <Share2 size={14} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
