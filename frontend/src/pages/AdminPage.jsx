import { useCallback, useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight, RefreshCw, Shield } from 'lucide-react'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import LoadingHint from '../components/ui/LoadingHint.jsx'

const PAGE_SIZE = 50

const STATUS_LABELS = {
  discussion: 'Обсуждение',
  active: 'Активна',
  completed: 'Завершена',
  cancelled: 'Отменена',
}

const STATUS_COLORS = {
  discussion: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  active: 'text-green-400 bg-green-400/10 border-green-400/20',
  completed: 'text-slate-400 bg-slate-400/10 border-slate-400/20',
  cancelled: 'text-red-400 bg-red-400/10 border-red-400/20',
}

const FILTERS = [
  { label: 'Активные', value: 'active' },
  { label: 'Обсуждение', value: 'discussion' },
  { label: 'Завершённые', value: 'completed' },
  { label: 'Отменённые', value: 'cancelled' },
  { label: 'Все', value: '' },
]

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function AdminPage() {
  const { isAdmin } = useAuth()
  const [exchanges, setExchanges] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('active')
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  const load = useCallback(
    async (currentPage) => {
      setLoading(true)
      setError(null)
      try {
        const params = { limit: PAGE_SIZE, offset: currentPage * PAGE_SIZE }
        if (filter) params.status = filter
        const data = await api.adminExchanges(params)
        setExchanges(data)
        setHasMore(data.length === PAGE_SIZE)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    },
    [filter]
  )

  useEffect(() => {
    if (!isAdmin) return
    // Загрузка списка при смене страницы/фильтра — ожидаемый паттерн для админ-таблицы
    // eslint-disable-next-line react-hooks/set-state-in-effect -- setState внутри async load()
    void load(page)
  }, [isAdmin, page, load])

  const setFilterAndReset = (value) => {
    setFilter(value)
    setPage(0)
  }

  if (!isAdmin) {
    return (
      <div className="animate-page flex min-h-[400px] items-center justify-center rounded-[40px] border border-white/5 bg-slate-950">
        <div className="text-center">
          <Shield className="mx-auto mb-3 text-red-500" size={40} />
          <p className="text-sm font-bold text-slate-400">Доступ запрещён</p>
          <p className="mt-1 text-xs text-slate-600">Требуется роль администратора</p>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-page space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="flex items-center gap-3 text-2xl font-black italic text-white sm:text-3xl">
            <Shield size={22} className="text-indigo-400" aria-hidden />
            ADMIN <span className="text-indigo-500">MODERATION</span>
          </h2>
          <p className="mt-1 text-xs text-slate-500">Мониторинг сделок платформы</p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="flex w-fit items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-xs font-bold text-slate-400 transition hover:bg-white/5 hover:text-white disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Обновить
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map(({ label, value }) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilterAndReset(value)}
            className={`rounded-xl px-4 py-2 text-[10px] font-black uppercase tracking-widest transition ${
              filter === value
                ? 'bg-indigo-600 text-white'
                : 'border border-white/10 text-slate-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error ? (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-xs text-red-300">
          {error}
        </div>
      ) : null}

      <div className="overflow-hidden rounded-[32px] border border-white/5 bg-slate-900">
        {loading ? (
          <div className="p-12">
            <LoadingHint label="Загружаем сделки…" />
          </div>
        ) : exchanges.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-sm font-bold text-slate-400">Нет сделок</p>
            <p className="mt-1 text-xs text-slate-600">По выбранному фильтру ничего не найдено</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/5 text-[10px] font-black uppercase tracking-widest text-slate-500">
                  <th className="px-5 py-4 text-left">#</th>
                  <th className="px-5 py-4 text-left">Инициатор → Партнёр</th>
                  <th className="px-5 py-4 text-left">Тип</th>
                  <th className="px-5 py-4 text-left">Статус</th>
                  <th className="px-5 py-4 text-left">Создана</th>
                  <th className="px-5 py-4 text-left">Начата</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {exchanges.map((ex) => (
                  <tr key={ex.id} className="transition hover:bg-white/[0.03]">
                    <td className="px-5 py-4 font-mono text-slate-500">#{ex.id}</td>
                    <td className="px-5 py-4">
                      <span className="font-bold text-white">
                        {ex.initiator_name ?? `#${ex.initiator_id}`}
                      </span>
                      <span className="mx-2 text-slate-600">→</span>
                      <span className="text-slate-300">
                        {ex.partner_name ?? (ex.partner_id ? `#${ex.partner_id}` : '—')}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-500">
                      {ex.listing_id ? `Листинг #${ex.listing_id}` : 'Прямой'}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase ${STATUS_COLORS[ex.status] ?? ''}`}
                      >
                        {STATUS_LABELS[ex.status] ?? ex.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-400">{formatDate(ex.created_at)}</td>
                    <td className="px-5 py-4 text-slate-400">{formatDate(ex.started_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-[10px] text-slate-600">
          Страница {page + 1} · показано {exchanges.length} сделок
        </p>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className="flex items-center gap-1 rounded-xl border border-white/10 px-3 py-2 text-[10px] font-bold text-slate-400 transition hover:bg-white/5 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronLeft size={14} />
            Назад
          </button>
          <span className="min-w-[2rem] text-center text-xs font-bold text-white">{page + 1}</span>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasMore || loading}
            className="flex items-center gap-1 rounded-xl border border-white/10 px-3 py-2 text-[10px] font-bold text-slate-400 transition hover:bg-white/5 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Вперёд
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdminPage
