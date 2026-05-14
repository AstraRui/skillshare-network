import { NavLink } from 'react-router-dom'
import {
  BarChart3,
  LayoutGrid,
  MessageSquare,
  Sparkles,
  User,
  Zap,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import { truncateEmail } from '../../lib/userDisplay.js'

const navItems = [
  { to: '/', label: 'Обзор', Icon: BarChart3, end: true },
  { to: '/deals', label: 'Сделки', Icon: LayoutGrid },
  { to: '/matching', label: 'Matching', Icon: Sparkles },
  { to: '/messages', label: 'Сообщения', Icon: MessageSquare },
  { to: '/profile', label: 'Профиль', Icon: User },
]

function Navigation() {
  const { isAuthenticated, userInitials, email } = useAuth()

  return (
    <nav className="fixed left-0 right-0 top-0 z-50 px-4 py-4 md:px-6" aria-label="Главная навигация">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 shadow-2xl backdrop-blur-xl md:flex-row md:items-center md:justify-between md:gap-0 md:px-6">
        <div className="flex items-center justify-between gap-3">
          <NavLink to="/" className="flex cursor-pointer items-center space-x-3" end>
            <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-fuchsia-500 p-2">
              <Zap className="size-5 fill-white text-white" strokeWidth={2.5} aria-hidden />
            </div>
            <span className="text-lg font-black uppercase tracking-tighter text-white md:text-xl">
              Skill
              <span className="bg-gradient-to-r from-indigo-400 to-fuchsia-400 bg-clip-text text-transparent">
                Share
              </span>
            </span>
          </NavLink>

          {isAuthenticated ? (
            <NavLink
              to="/profile"
              className="flex shrink-0 items-center space-x-3 rounded-xl border border-white/10 bg-white/5 p-1.5 transition hover:bg-white/10 md:hidden"
            >
              <div className="flex size-7 items-center justify-center rounded-lg bg-indigo-600 text-[10px] font-bold text-white">
                {userInitials}
              </div>
            </NavLink>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center justify-center gap-1 sm:gap-2 md:flex-1 md:justify-center md:gap-0 md:space-x-6">
          {navItems.map(({ to, label, Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                [
                  'flex items-center space-x-2 rounded-lg px-3 py-2 text-[11px] font-black uppercase tracking-widest transition-all',
                  isActive
                    ? 'bg-indigo-500/10 text-indigo-400 shadow-[inset_0_0_10px_rgba(99,102,241,0.2)]'
                    : 'text-slate-400 hover:text-white',
                ].join(' ')
              }
            >
              <Icon size={14} strokeWidth={2.5} aria-hidden />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>

        {isAuthenticated ? (
          <div className="hidden items-center justify-end space-x-4 md:flex md:shrink-0">
            <NavLink
              to="/profile"
              className="flex items-center space-x-3 rounded-xl border border-white/10 bg-white/5 p-1.5 transition hover:bg-white/10"
            >
              <div className="flex size-7 items-center justify-center rounded-lg bg-indigo-600 text-[10px] font-bold text-white">
                {userInitials}
              </div>
              {email ? (
                <div className="hidden pr-2 text-left lg:block">
                  <p className="max-w-[140px] truncate text-[10px] font-black leading-none text-white">
                    {truncateEmail(email, 24)}
                  </p>
                  <p className="text-[8px] uppercase tracking-tighter text-slate-500">Аккаунт</p>
                </div>
              ) : null}
            </NavLink>
          </div>
        ) : null}
      </div>
    </nav>
  )
}

export default Navigation
