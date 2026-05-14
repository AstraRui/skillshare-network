import { useCallback, useEffect, useState } from 'react'
import {
  MoreVertical,
  Paperclip,
  Search,
  Send,
  Smile,
} from 'lucide-react'
import LoadingHint from '../components/ui/LoadingHint.jsx'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

const mockChats = [
  { id: 1, name: 'Мария К. (Dev)', last: 'Когда созвонимся по API?', time: '12:45' },
  { id: 2, name: 'Игорь С. (Legal)', last: 'Договор во вложении', time: 'Вчера' },
  { id: 3, name: 'Анна В. (SMM)', last: 'Презентация готова', time: '02.05' },
]

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const statusLabel = {
  discussion: 'Обсуждение',
  active: 'Active Swap',
  completed: 'Завершено',
  cancelled: 'Отменено',
}

function MessagesPage() {
  const { isAuthenticated, userId } = useAuth()
  const [demoChatId, setDemoChatId] = useState(1)
  const [exchanges, setExchanges] = useState([])
  const [listingsById, setListingsById] = useState({})
  const [selectedId, setSelectedId] = useState(null)
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState(null)
  const [loadingList, setLoadingList] = useState(false)
  const [loadingMsg, setLoadingMsg] = useState(false)

  const loadExchanges = useCallback(async () => {
    if (!isAuthenticated) return
    setLoadingList(true)
    setError(null)
    try {
      const [ex, lists] = await Promise.all([api.myExchanges(), api.listings({})])
      const map = {}
      for (const l of lists) map[l.id] = l
      setListingsById(map)
      setExchanges(ex)
      setSelectedId((prev) => {
        if (prev != null && ex.some((e) => e.id === prev)) return prev
        return ex[0]?.id ?? null
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoadingList(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    queueMicrotask(() => {
      void loadExchanges()
    })
  }, [loadExchanges])

  const loadMessages = useCallback(async (exchangeId) => {
    if (!exchangeId || !isAuthenticated) return
    setLoadingMsg(true)
    setError(null)
    try {
      const list = await api.exchangeMessages(exchangeId)
      setMessages(list)
    } catch (e) {
      setError(e.message)
      setMessages([])
    } finally {
      setLoadingMsg(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (selectedId == null) return
    queueMicrotask(() => {
      void loadMessages(selectedId)
    })
  }, [selectedId, loadMessages])

  const selected = exchanges.find((e) => e.id === selectedId)
  const title = selected?.listing_id
    ? listingsById[selected.listing_id]?.title ?? `Сделка #${selected.id}`
    : selected
      ? `Сделка #${selected.id}`
      : 'Чат'

  const send = async () => {
    const text = draft.trim()
    if (!text || !selectedId) return
    try {
      await api.postExchangeMessage(selectedId, text)
      setDraft('')
      await loadMessages(selectedId)
    } catch (e) {
      setError(e.message)
    }
  }

  const confirmDone = async () => {
    if (!selectedId) return
    try {
      await api.confirmExchangeCompletion(selectedId)
      await loadExchanges()
      await loadMessages(selectedId)
    } catch (e) {
      setError(e.message)
    }
  }

  const useApi = isAuthenticated && exchanges.length > 0
  const sidebarItems = useApi
    ? exchanges.map((ex) => ({
        id: ex.id,
        name: ex.listing_id
          ? listingsById[ex.listing_id]?.title ?? `Обмен #${ex.id}`
          : `Обмен #${ex.id}`,
        last: statusLabel[ex.status] ?? ex.status,
        time: '',
      }))
    : mockChats

  const effectiveSelected = useApi ? selectedId : demoChatId

  return (
    <div className="animate-page flex h-[min(700px,calc(100vh-10rem))] flex-col overflow-hidden rounded-[40px] border border-white/5 bg-slate-950/50 backdrop-blur-md md:flex-row">
      <div className="flex w-full shrink-0 flex-col border-white/5 bg-slate-900/30 md:w-80 md:border-r">
        <div className="p-6">
          <h2 className="mb-4 text-xl font-black italic text-white">MESSAGES</h2>
          <div className="relative">
            <Search
              className="absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-slate-500"
              aria-hidden
            />
            <input
              type="search"
              placeholder="Поиск сделок..."
              className="w-full rounded-xl border border-white/10 bg-white/5 py-2 pl-9 pr-4 text-xs text-white outline-none ring-indigo-500 focus:ring-1"
            />
          </div>
        </div>
        <div className="custom-scrollbar flex-1 space-y-1 overflow-y-auto px-3 pb-4">
          {!isAuthenticated ? (
            <p className="px-2 text-xs text-slate-500">Войдите, чтобы видеть сделки с сервера.</p>
          ) : null}
          {loadingList ? (
            <div className="px-2">
              <LoadingHint label="Загрузка списка…" />
            </div>
          ) : null}
          {sidebarItems.map((chat) => (
            <button
              key={chat.id}
              type="button"
              onClick={() => (useApi ? setSelectedId(chat.id) : setDemoChatId(chat.id))}
              className={`flex w-full items-center space-x-3 rounded-2xl p-4 text-left transition-all ${
                effectiveSelected === chat.id
                  ? 'border border-indigo-500/20 bg-indigo-600/10'
                  : 'border border-transparent hover:bg-white/5'
              }`}
            >
              <div
                className={`flex size-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                  effectiveSelected === chat.id ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                }`}
              >
                {String(chat.name).charAt(0)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex justify-between gap-2">
                  <p
                    className={`truncate text-xs font-bold ${
                      effectiveSelected === chat.id ? 'text-white' : 'text-slate-300'
                    }`}
                  >
                    {chat.name}
                  </p>
                  {chat.time ? (
                    <span className="shrink-0 text-[8px] text-slate-500">{chat.time}</span>
                  ) : null}
                </div>
                <p className="mt-1 truncate text-[10px] font-medium text-slate-500">{chat.last}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col bg-slate-900/10">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/5 p-4 sm:p-6">
          <div className="flex min-w-0 items-center space-x-4">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-lg font-black text-white">
              M
            </div>
            <div className="min-w-0">
              <h3 className="truncate text-sm font-bold text-white">Мария Кузнецова</h3>
              <div className="flex items-center space-x-2">
                <span className="size-1.5 shrink-0 animate-pulse rounded-full bg-green-500" />
                <span className="truncate text-[10px] font-bold uppercase tracking-widest text-slate-500">
                  {selected ? `${statusLabel[selected.status] ?? selected.status}: ${title}` : 'Демо-чат'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="p-2 text-slate-400 transition hover:text-white"
              aria-label="Поиск"
            >
              <Search size={18} />
            </button>
            <button
              type="button"
              className="p-2 text-slate-400 transition hover:text-white"
              aria-label="Меню"
            >
              <MoreVertical size={18} />
            </button>
            {useApi && selected?.status === 'active' ? (
              <button
                type="button"
                onClick={confirmDone}
                className="rounded-xl bg-indigo-600 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500"
              >
                Подтвердить выполнение
              </button>
            ) : (
              <button
                type="button"
                className="rounded-xl bg-indigo-600 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-white shadow-lg shadow-indigo-500/20"
              >
                Завершить сделку
              </button>
            )}
          </div>
        </div>

        {error ? (
          <div className="border-b border-red-500/20 bg-red-500/10 px-4 py-2 text-xs text-red-200">
            {error}
          </div>
        ) : null}

        <div className="custom-scrollbar flex-1 space-y-6 overflow-y-auto bg-[radial-gradient(ellipse_at_center,#6366f105,transparent)] p-4 sm:p-6">
          {useApi && loadingMsg ? (
            <div className="px-1">
              <LoadingHint label="Загрузка сообщений…" />
            </div>
          ) : null}
          {useApi && messages.length === 0 && !loadingMsg ? (
            <p className="text-xs text-slate-500">Пока нет сообщений — напишите первым.</p>
          ) : null}
          {useApi
            ? messages.map((msg) => {
                const mine = msg.sender_id === userId
                return (
                  <div
                    key={msg.id}
                    className={`max-w-[85%] text-sm leading-relaxed sm:max-w-[60%] ${
                      mine
                        ? 'ml-auto rounded-3xl rounded-tr-none bg-indigo-600 p-4 text-white shadow-2xl shadow-indigo-500/20'
                        : 'rounded-3xl rounded-tl-none border border-white/5 bg-white/5 p-4 text-slate-200 shadow-xl'
                    }`}
                  >
                    {msg.content}
                    <p
                      className={`mt-2 font-mono text-[9px] ${mine ? 'text-right text-indigo-300' : 'text-slate-500'}`}
                    >
                      {formatTime(msg.created_at)}
                      {mine ? ' • Отправлено' : ''}
                    </p>
                  </div>
                )
              })
            : [
                <div
                  key="1"
                  className="max-w-[85%] rounded-3xl rounded-tl-none border border-white/5 bg-white/5 p-4 text-sm leading-relaxed text-slate-200 shadow-xl sm:max-w-[60%]"
                >
                  Привет! Я закончила базовую логику на Python. Нам нужно обсудить фронтенд часть,
                  чтобы я знала какие эндпоинты тебе нужны в первую очередь.
                  <p className="mt-2 font-mono text-[9px] text-slate-500">12:30</p>
                </div>,
                <div
                  key="2"
                  className="ml-auto max-w-[85%] rounded-3xl rounded-tr-none bg-indigo-600 p-4 text-sm leading-relaxed text-white shadow-2xl shadow-indigo-500/20 sm:max-w-[60%]"
                >
                  Супер! Мне важно сначала получить эндпоинты для авторизации и профиля. Дизайн я
                  уже залил в Фигму, можешь посмотреть?
                  <p className="mt-2 text-right font-mono text-[9px] text-indigo-300">
                    12:34 • Прочитано
                  </p>
                </div>,
                <div key="3" className="flex justify-center">
                  <span className="rounded-full border border-white/10 bg-white/5 px-4 py-1 text-[9px] font-bold uppercase tracking-widest text-slate-500">
                    Среда, 06 Мая
                  </span>
                </div>,
                <div
                  key="4"
                  className="max-w-[85%] rounded-3xl rounded-tl-none border border-white/5 bg-white/5 p-4 text-sm leading-relaxed text-slate-200 sm:max-w-[60%]"
                >
                  Да, посмотрела. Дизайн огонь! Давай завтра в 11:00 созвонимся.
                  <p className="mt-2 font-mono text-[9px] text-slate-500">12:45</p>
                </div>,
              ]}
        </div>

        <div className="border-t border-white/5 bg-slate-900/50 p-4 sm:p-6">
          <div className="flex items-center space-x-2 rounded-[24px] border border-white/10 bg-white/5 p-2">
            <button
              type="button"
              className="p-2 text-slate-500 transition hover:text-indigo-400"
              aria-label="Вложение"
            >
              <Paperclip size={18} />
            </button>
            <input
              type="text"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="Введите сообщение..."
              disabled={!useApi || !selectedId}
              className="min-w-0 flex-1 border-none bg-transparent px-2 text-sm text-white outline-none ring-0 placeholder:text-slate-600"
            />
            <button
              type="button"
              className="p-2 text-slate-500 transition hover:text-indigo-400"
              aria-label="Эмодзи"
            >
              <Smile size={18} />
            </button>
            <button
              type="button"
              onClick={send}
              disabled={!useApi || !selectedId}
              className="rounded-2xl bg-indigo-600 p-3 text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500 disabled:opacity-40"
              aria-label="Отправить"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MessagesPage
