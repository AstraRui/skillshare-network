import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import LoadingHint from '../components/ui/LoadingHint.jsx'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

const userProfile = {
  reputation: 4.92,
}

const statusProgress = {
  discussion: 45,
  active: 78,
  completed: 100,
  cancelled: 0,
}

const mockSwaps = [
  { title: 'Python API', partner: 'Мария К.', progress: 85 },
  { title: 'Legal Audit', partner: 'Игорь С.', progress: 40 },
]

const systemLogs = [
  { text: 'Мария К. начала разработку API', time: '12:45', type: 'msg' },
  { text: 'Алгоритм обновил 5 связей', time: '11:20', type: 'system' },
  { text: 'Верификация пройдена успешно', time: 'Вчера', type: 'security' },
  { text: 'Новая цепочка: Вы -> Мария -> Игорь', time: '02.05', type: 'match' },
]

function DashboardPage() {
  const { isAuthenticated } = useAuth()
  const [exchanges, setExchanges] = useState([])
  const [listingsById, setListingsById] = useState({})
  const [loadError, setLoadError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) return
    let cancelled = false
    ;(async () => {
      setLoading(true)
      try {
        const [ex, lists] = await Promise.all([api.myExchanges(), api.listings({})])
        if (cancelled) return
        setExchanges(ex.filter((e) => e.status === 'discussion' || e.status === 'active'))
        const map = {}
        for (const l of lists) map[l.id] = l
        setListingsById(map)
        setLoadError(null)
      } catch (e) {
        if (!cancelled) setLoadError(e.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [isAuthenticated])

  const swaps = useMemo(() => {
    if (!isAuthenticated || exchanges.length === 0) return mockSwaps
    return exchanges.slice(0, 4).map((ex) => ({
      title: ex.listing_id
        ? listingsById[ex.listing_id]?.title ?? `Сделка #${ex.id}`
        : `Сделка #${ex.id}`,
      partner: 'Участник сделки',
      progress: statusProgress[ex.status] ?? 40,
    }))
  }, [isAuthenticated, exchanges, listingsById])

  return (
    <div className="animate-page mt-6 grid grid-cols-1 gap-8 lg:mt-10 lg:grid-cols-3">
      <div className="space-y-8 lg:col-span-2">
        {loadError ? (
          <p className="rounded-2xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
            {loadError}
          </p>
        ) : null}
        {isAuthenticated && loading ? <LoadingHint label="Подтягиваем сделки…" /> : null}
        {!isAuthenticated ? (
          <p className="text-sm text-slate-500">
            Войдите в профиль, чтобы подтянуть активные сделки с бэкенда.
          </p>
        ) : null}

        <div className="group relative overflow-hidden rounded-[40px] border border-white/5 bg-slate-900 p-10 text-white shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-transparent opacity-0 transition-opacity duration-700 group-hover:opacity-100" />
          <div className="relative z-10 flex flex-col items-center justify-between gap-8 md:flex-row">
            <div className="text-center md:text-left">
              <span className="inline-block rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-indigo-400">
                Pro Member
              </span>
              <h1 className="mt-4 text-4xl font-black uppercase italic leading-none tracking-tighter text-white sm:text-5xl">
                Network <br /> Efficiency <span className="text-indigo-400">+40%</span>
              </h1>
              <p className="mt-4 max-w-sm font-medium text-slate-400">
                Алгоритм пересчитал цепочки. Найдено 3 новых элитных совпадения.
              </p>
            </div>
            <div className="shrink-0 rotate-3 rounded-[32px] border border-white/10 bg-slate-800 p-8 shadow-2xl transition-transform duration-500 group-hover:rotate-0">
              <div className="text-4xl font-black text-indigo-400">{userProfile.reputation}</div>
              <div className="mt-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                Trust Score
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-[32px] border border-white/5 bg-slate-900/50 p-8 backdrop-blur-md">
            <h3 className="mb-6 text-lg font-bold uppercase italic text-white">Active Swaps</h3>
            <div className="space-y-4">
              {swaps.map((swap, i) => (
                <div
                  key={`${swap.title}-${i}`}
                  className="group rounded-2xl border border-white/5 bg-white/5 p-4 transition hover:border-indigo-500/30"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-bold text-white">{swap.title}</p>
                      <p className="text-[10px] text-slate-500">{swap.partner}</p>
                    </div>
                    <div className="font-mono text-[10px] text-indigo-400">{swap.progress}%</div>
                  </div>
                  <div className="h-1 w-full overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full bg-indigo-500 transition-all duration-1000"
                      style={{ width: `${swap.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-col justify-between rounded-[32px] bg-gradient-to-br from-indigo-600 to-fuchsia-600 p-8 shadow-2xl shadow-indigo-500/20">
            <h3 className="text-lg font-bold uppercase italic text-white">
              Matching <br /> Pulse
            </h3>
            <p className="text-sm font-medium text-white/80">
              Спрос на ваш навык UI/UX вырос на 15% в секторе LegalTech. Пора обновиться!
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
            {systemLogs.map((n, i) => (
              <div
                key={i}
                className="group flex cursor-pointer items-start space-x-3 border-l-2 border-transparent pl-3 transition-all hover:border-indigo-500"
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
                  <span className="mt-1 block font-mono text-[9px] uppercase text-slate-600">
                    {n.time}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <button
            type="button"
            className="mt-8 w-full rounded-xl border border-white/5 bg-white/5 py-3 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-white/10"
          >
            Архив логов
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
