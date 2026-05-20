import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import LoadingHint from '../components/ui/LoadingHint.jsx'
import { api } from '../api/client.js'
import {
  buildSystemLogs,
  matchCountLabel,
  matchingPulseText,
  networkEfficiencyPercent,
} from '../lib/dashboardActivity.js'
import { useAuth } from '../context/AuthContext.jsx'

const statusProgress = {
  discussion: 45,
  active: 78,
  completed: 100,
  cancelled: 0,
}

function DashboardPage() {
  const { isAuthenticated } = useAuth()
  const [profile, setProfile] = useState(null)
  const [exchanges, setExchanges] = useState([])
  const [matches, setMatches] = useState(null)
  const [skills, setSkills] = useState(null)
  const [incoming, setIncoming] = useState([])
  const [loadError, setLoadError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) return
    let cancelled = false
    queueMicrotask(() => {
      void (async () => {
      setLoading(true)
      setLoadError(null)
      try {
        const [prof, ex, matchRes, skillRes, incomingRes] = await Promise.all([
          api.myProfile(),
          api.myExchanges(),
          api.matches(),
          api.mySkills(),
          api.incomingInterests(),
        ])
        if (cancelled) return
        setProfile(prof)
        setExchanges(ex)
        setMatches(matchRes)
        setSkills(skillRes)
        setIncoming(incomingRes)
      } catch (e) {
        if (!cancelled) setLoadError(e.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
      })()
    })
    return () => {
      cancelled = true
    }
  }, [isAuthenticated])

  const activeExchanges = useMemo(
    () => exchanges.filter((e) => e.status === 'discussion' || e.status === 'active'),
    [exchanges],
  )

  const swaps = useMemo(() => {
    return activeExchanges.slice(0, 4).map((ex) => ({
      id: ex.id,
      title: ex.listing_title ?? `Сделка #${ex.id}`,
      partner: ex.partner_full_name?.trim() || 'Участник сделки',
      progress: statusProgress[ex.status] ?? 40,
    }))
  }, [activeExchanges])

  const systemLogs = useMemo(
    () =>
      buildSystemLogs({
        incoming,
        exchanges: activeExchanges,
        matchTotal: matches?.total ?? 0,
      }),
    [incoming, activeExchanges, matches?.total],
  )

  const efficiency = networkEfficiencyPercent(matches)
  const memberBadge =
    profile && profile.exchanges_count > 0 ? 'Active Member' : 'Участник'

  return (
    <div className="animate-page mt-6 grid grid-cols-1 gap-8 lg:mt-10 lg:grid-cols-3">
      <div className="space-y-8 lg:col-span-2">
        {loadError ? (
          <p className="rounded-2xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
            {loadError}
          </p>
        ) : null}
        {isAuthenticated && loading ? <LoadingHint label="Загрузка обзора…" /> : null}
        {!isAuthenticated ? (
          <p className="text-sm text-slate-500">
            <Link to="/profile" className="text-indigo-400 hover:text-indigo-300">
              Войдите
            </Link>
            , чтобы увидеть сделки, matching и активность с сервера.
          </p>
        ) : null}

        <div className="group relative overflow-hidden rounded-[40px] border border-white/5 bg-slate-900 p-10 text-white shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-transparent opacity-0 transition-opacity duration-700 group-hover:opacity-100" />
          <div className="relative z-10 flex flex-col items-center justify-between gap-8 md:flex-row">
            <div className="text-center md:text-left">
              <span className="inline-block rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-indigo-400">
                {isAuthenticated && profile ? memberBadge : 'Гость'}
              </span>
              <h1 className="mt-4 text-4xl font-black uppercase italic leading-none tracking-tighter text-white sm:text-5xl">
                Network <br /> Efficiency{' '}
                <span className="text-indigo-400">
                  {isAuthenticated && efficiency != null ? `+${efficiency}%` : '—'}
                </span>
              </h1>
              <p className="mt-4 max-w-sm font-medium text-slate-400">
                {isAuthenticated && matches != null
                  ? matchCountLabel(matches.total)
                  : 'Войдите, чтобы увидеть совпадения по навыкам.'}
              </p>
            </div>
            <div className="shrink-0 rotate-3 rounded-[32px] border border-white/10 bg-slate-800 p-8 shadow-2xl transition-transform duration-500 group-hover:rotate-0">
              <div className="text-4xl font-black text-indigo-400">
                {isAuthenticated && profile ? profile.rating.toFixed(2) : '—'}
              </div>
              <div className="mt-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                Trust Score
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-[32px] border border-white/5 bg-slate-900/50 p-8 backdrop-blur-md">
            <h3 className="mb-6 text-lg font-bold uppercase italic text-white">Active Swaps</h3>
            {isAuthenticated && !loading && swaps.length === 0 && !loadError ? (
              <p className="mb-4 text-xs text-slate-500">
                Нет активных сделок. Откликнитесь на заказ в{' '}
                <Link to="/deals" className="text-indigo-400 hover:text-indigo-300">
                  каталоге
                </Link>{' '}
                или примите отклик в{' '}
                <Link to="/messages" className="text-indigo-400 hover:text-indigo-300">
                  сообщениях
                </Link>
                .
              </p>
            ) : null}
            <div className="space-y-4">
              {swaps.map((swap) => (
                <Link
                  key={swap.id}
                  to="/messages"
                  className="group block rounded-2xl border border-white/5 bg-white/5 p-4 transition hover:border-indigo-500/30"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-bold text-white">{swap.title}</p>
                      <p className="text-[10px] text-slate-500">{swap.partner}</p>
                    </div>
                    <div className="font-mono text-[10px] text-indigo-400">
                      {swap.progress}%
                    </div>
                  </div>
                  <div className="h-1 w-full overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full bg-indigo-500 transition-all duration-1000"
                      style={{ width: `${swap.progress}%` }}
                    />
                  </div>
                </Link>
              ))}
            </div>
          </div>
          <div className="flex flex-col justify-between rounded-[32px] bg-gradient-to-br from-indigo-600 to-fuchsia-600 p-8 shadow-2xl shadow-indigo-500/20">
            <h3 className="text-lg font-bold uppercase italic text-white">
              Matching <br /> Pulse
            </h3>
            <p className="text-sm font-medium text-white/80">
              {isAuthenticated && !loading && skills && matches != null
                ? matchingPulseText({ skills, matches })
                : 'Загрузка insights по навыкам…'}
            </p>
            <Link
              to="/matching"
              className="mt-4 w-full rounded-xl bg-white py-3 text-center text-xs font-black uppercase tracking-widest text-indigo-900 shadow-xl transition-transform hover:scale-105 active:scale-95"
            >
              Запустить Граф
            </Link>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="h-full rounded-[40px] border border-white/5 bg-slate-900 p-8 shadow-2xl">
          <h3 className="mb-6 text-sm font-black uppercase italic tracking-widest text-white">
            System Logs
          </h3>
          <div className="custom-scrollbar max-h-[400px] space-y-6 overflow-y-auto pr-2">
            {isAuthenticated && !loading && systemLogs.length === 0 ? (
              <p className="text-xs text-slate-500">Пока нет событий — отклики и сделки появятся здесь.</p>
            ) : null}
            {systemLogs.map((n, i) => (
              <div
                key={`${n.text}-${i}`}
                className="group flex cursor-default items-start space-x-3 border-l-2 border-transparent pl-3 transition-all hover:border-indigo-500"
              >
                <div
                  className={`mt-1.5 size-1.5 shrink-0 rounded-full ${
                    n.type === 'msg'
                      ? 'bg-indigo-500'
                      : n.type === 'match'
                        ? 'bg-fuchsia-500'
                        : 'bg-slate-500'
                  }`}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs leading-relaxed text-slate-300 transition-colors group-hover:text-white">
                    {n.text}
                  </p>
                  {n.time ? (
                    <span className="mt-1 block font-mono text-[9px] uppercase text-slate-600">
                      {n.time}
                    </span>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
          <Link
            to="/messages"
            className="mt-8 block w-full rounded-xl border border-white/5 bg-white/5 py-3 text-center text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-white/10"
          >
            Сообщения и сделки
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
