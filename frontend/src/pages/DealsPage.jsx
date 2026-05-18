import { useCallback, useEffect, useMemo, useState } from 'react'
import { Search, X } from 'lucide-react'
import LoadingHint from '../components/ui/LoadingHint.jsx'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

const mockOffers = [
  {
    id: 'm1',
    user: 'Мария К.',
    role: 'Senior Python Dev',
    offer: 'Обучение Python с нуля',
    seeking: 'UI/UX Дизайн',
    tags: ['Education', 'Python'],
    type: 'mentorship',
  },
  {
    id: 'm2',
    user: 'Анна В.',
    role: 'SMM Lead',
    offer: 'Стратегия продвижения на 3 мес.',
    seeking: 'Юридический аудит',
    tags: ['Marketing', 'SMM'],
    type: 'service',
  },
  {
    id: 'm3',
    user: 'Игорь С.',
    role: 'Legal Tech',
    offer: 'Договор и регламенты',
    seeking: 'Редизайн лендинга',
    tags: ['Legal', 'Docs'],
    type: 'service',
  },
]

function listingToOffer(listing) {
  const blob = `${listing.title} ${listing.description ?? ''} ${listing.offering_summary}`
  const mentorship = /ментор|обучен|курс|коуч/i.test(blob)
  const words = listing.title
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w.replace(/[^a-zA-Zа-яА-ЯёЁ0-9]/g, ''))
    .filter(Boolean)
  const tags = [
    ...(words.length ? words.map((w) => w.slice(0, 12)) : ['Offer']),
    `id${listing.id}`,
  ].slice(0, 4)

  return {
    id: listing.id,
    user: `Автор #${listing.author_id}`,
    role: listing.title,
    offer: listing.offering_summary,
    seeking: listing.seeking_summary,
    tags,
    type: mentorship ? 'mentorship' : 'service',
  }
}

function DealsPage() {
  const { isAuthenticated, openAuthModal } = useAuth()
  const [query, setQuery] = useState('')
  const [offers, setOffers] = useState([])
  const [fromApi, setFromApi] = useState(false)
  const [loadError, setLoadError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  const load = useCallback(async () => {
    setLoadError(null)
    setLoading(true)
    try {
      const rows = await api.listings({})
      if (rows.length) {
        setOffers(rows.map(listingToOffer))
        setFromApi(true)
      } else {
        setOffers(mockOffers)
        setFromApi(false)
      }
    } catch (e) {
      setLoadError(e.message)
      setOffers(mockOffers)
      setFromApi(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    queueMicrotask(() => {
      void load()
    })
  }, [load])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return offers
    return offers.filter(
      (o) =>
        o.user.toLowerCase().includes(q) ||
        o.role.toLowerCase().includes(q) ||
        o.offer.toLowerCase().includes(q) ||
        o.seeking.toLowerCase().includes(q) ||
        o.tags.some((t) => t.toLowerCase().includes(q)),
    )
  }, [offers, query])

  return (
    <div className="animate-page space-y-8">
      <div className="flex flex-col items-end justify-between gap-6 md:flex-row">
        <div>
          <h2 className="text-3xl font-black uppercase italic tracking-tighter text-white sm:text-4xl">
            Global <span className="text-indigo-500">Market</span>
          </h2>
          <p className="mt-2 text-sm text-slate-500">Каталог открытых предложений в сети.</p>
          {loading ? (
            <div className="mt-2">
              <LoadingHint label="Загружаем каталог…" />
            </div>
          ) : null}
          {loadError ? (
            <p className="mt-2 text-xs text-amber-400/90">
              API: {loadError} — показаны демо-карточки.
            </p>
          ) : null}
          {fromApi ? (
            <p className="mt-1 text-[10px] font-bold uppercase tracking-widest text-slate-600">
              Загружено с сервера
            </p>
          ) : null}
        </div>

        <div className="relative w-full md:w-64">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-500"
            aria-hidden
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск навыка..."
            className="w-full rounded-xl border border-white/10 bg-white/5 py-3 pl-10 pr-4 text-sm text-white outline-none transition-colors placeholder:text-slate-600 focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((offer) => (
          <button
            key={offer.id}
            type="button"
            onClick={() => {
              if (!isAuthenticated) {
                openAuthModal()
                return
              }
              setSelected(offer)
            }}
            className="group relative cursor-pointer overflow-hidden rounded-[32px] border border-white/5 bg-slate-900/40 p-6 text-left transition-all duration-300 hover:-translate-y-2 hover:border-indigo-500/40 hover:bg-slate-800/60 hover:shadow-[0_15px_40px_-10px_rgba(99,102,241,0.3)]"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

            {offer.type === 'mentorship' ? (
              <div className="absolute right-0 top-0 z-10 rounded-bl-2xl bg-gradient-to-r from-indigo-600 to-fuchsia-600 px-4 py-1.5 text-[8px] font-black uppercase tracking-widest text-white shadow-lg">
                Менторство
              </div>
            ) : null}

            <div className="relative z-10 mb-6 flex items-center space-x-3">
              <div className="flex size-10 items-center justify-center rounded-xl border border-white/10 bg-slate-800 text-sm font-bold text-indigo-400 shadow-inner">
                {offer.user.charAt(0)}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{offer.user}</h4>
                <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500">
                  {offer.role}
                </p>
              </div>
            </div>

            <div className="relative z-10 space-y-4">
              <div>
                <p className="mb-1 text-[10px] font-black uppercase text-slate-500">Предлагает:</p>
                <p className="text-sm font-bold text-white">{offer.offer}</p>
              </div>

              <div className="my-2 h-px w-full bg-gradient-to-r from-transparent via-slate-700 to-transparent" />

              <div>
                <p className="mb-1 text-[10px] font-black uppercase text-slate-500">Ищет:</p>
                <p className="text-sm font-bold text-fuchsia-400">{offer.seeking}</p>
              </div>
            </div>

            <div className="relative z-10 mt-6 flex flex-wrap gap-2 border-t border-white/5 pt-6">
              {offer.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-md border border-white/5 bg-black/40 px-2.5 py-1 font-mono text-[9px] font-bold text-slate-400 transition-colors group-hover:border-indigo-500/30 group-hover:text-indigo-300"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>

      {selected ? (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="deal-modal-title"
        >
          <div className="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-[32px] border border-white/10 bg-slate-900 p-6 shadow-2xl">
            <button
              type="button"
              onClick={() => setSelected(null)}
              className="absolute right-4 top-4 rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
              aria-label="Закрыть"
            >
              <X size={20} />
            </button>
            <h3 id="deal-modal-title" className="pr-10 text-xl font-black text-white">
              {selected.role}
            </h3>
            <p className="mt-1 text-xs text-slate-500">{selected.user}</p>
            <div className="mt-6 space-y-4 text-sm">
              <div>
                <p className="text-[10px] font-black uppercase text-slate-500">Предлагает</p>
                <p className="font-bold text-white">{selected.offer}</p>
              </div>
              <div>
                <p className="text-[10px] font-black uppercase text-slate-500">Ищет</p>
                <p className="font-bold text-fuchsia-400">{selected.seeking}</p>
              </div>
            </div>
            <p className="mt-6 text-xs text-slate-500">
              Отклик и создание сделки — через профиль и API интересов к объявлению.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default DealsPage
