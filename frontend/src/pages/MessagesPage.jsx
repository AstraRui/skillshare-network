import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
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
  const { userId } = useAuth()
  const [exchanges, setExchanges] = useState([])
  const [incomingInterests, setIncomingInterests] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState(null)
  const [loadingList, setLoadingList] = useState(false)
  const [loadingMsg, setLoadingMsg] = useState(false)
  const [acceptBusyId, setAcceptBusyId] = useState(null)
  const [actionBusy, setActionBusy] = useState(false)
  const [myReview, setMyReview] = useState(null)
  const [reviewRating, setReviewRating] = useState(5)
  const [reviewComment, setReviewComment] = useState('')
  const [reviewFeedback, setReviewFeedback] = useState(null)

  const loadExchanges = useCallback(async () => {
    setLoadingList(true)
    setError(null)
    try {
      const [ex, incoming] = await Promise.all([api.myExchanges(), api.incomingInterests()])
      setIncomingInterests(incoming)
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
  }, [])

  useEffect(() => {
    queueMicrotask(() => {
      void loadExchanges()
    })
  }, [loadExchanges])

  const loadMessages = useCallback(async (exchangeId) => {
    if (!exchangeId) return
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
  }, [])

  useEffect(() => {
    if (selectedId == null) return
    queueMicrotask(() => {
      void loadMessages(selectedId)
    })
  }, [selectedId, loadMessages])

  useEffect(() => {
    if (selectedId == null) return
    const exchange = exchanges.find((e) => e.id === selectedId)
    let cancelled = false
    queueMicrotask(() => {
      if (exchange?.status !== 'completed') {
        setMyReview(null)
        return
      }
      void api
        .myExchangeReview(selectedId)
        .then((review) => {
          if (!cancelled) setMyReview(review)
        })
        .catch(() => {
          if (!cancelled) setMyReview(null)
        })
    })
    return () => {
      cancelled = true
    }
  }, [selectedId, exchanges])

  const acceptIncoming = async (item) => {
    setAcceptBusyId(item.id)
    setError(null)
    try {
      const exchange = await api.acceptListingInterest(item.listing_id, item.responder_id)
      await loadExchanges()
      setSelectedId(exchange.id)
      await loadMessages(exchange.id)
    } catch (e) {
      setError(e.message)
    } finally {
      setAcceptBusyId(null)
    }
  }

  const selected = exchanges.find((e) => e.id === selectedId)
  const title = selected?.listing_title ?? (selected ? `Сделка #${selected.id}` : 'Чат')

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
    setActionBusy(true)
    setError(null)
    try {
      await api.confirmExchangeCompletion(selectedId)
      await loadExchanges()
      await loadMessages(selectedId)
    } catch (e) {
      setError(e.message)
    } finally {
      setActionBusy(false)
    }
  }

  const startActiveSwap = async () => {
    if (!selectedId) return
    setActionBusy(true)
    setError(null)
    try {
      await api.updateExchangeStatus(selectedId, 'active')
      await loadExchanges()
    } catch (e) {
      setError(e.message)
    } finally {
      setActionBusy(false)
    }
  }

  const submitReview = async () => {
    if (!selectedId) return
    setActionBusy(true)
    setReviewFeedback(null)
    setError(null)
    try {
      const review = await api.submitExchangeReview(selectedId, {
        rating: reviewRating,
        comment: reviewComment.trim() || null,
      })
      setMyReview(review)
      setReviewFeedback({ type: 'ok', text: 'Спасибо! Отзыв сохранён.' })
    } catch (e) {
      setReviewFeedback({ type: 'err', text: e.message })
    } finally {
      setActionBusy(false)
    }
  }

  const iAmInitiator = selected?.initiator_id === userId
  const myConfirmed = iAmInitiator
    ? selected?.completed_by_initiator
    : selected?.completed_by_partner
  const partnerConfirmed = iAmInitiator
    ? selected?.completed_by_partner
    : selected?.completed_by_initiator

  const sidebarItems = exchanges.map((ex) => ({
    id: ex.id,
    name: ex.partner_full_name
      ? `${ex.partner_full_name}`
      : ex.listing_title ?? `Сделка #${ex.id}`,
    subtitle: ex.listing_title ?? '',
    last: statusLabel[ex.status] ?? ex.status,
    time: '',
  }))

  const hasSelection = selectedId != null && exchanges.some((e) => e.id === selectedId)

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
          {!loadingList && incomingInterests.length > 0 ? (
            <div className="mb-3 space-y-2 rounded-2xl border border-amber-500/20 bg-amber-500/5 p-3">
              <p className="text-[10px] font-black uppercase tracking-widest text-amber-300">
                Входящие отклики ({incomingInterests.length})
              </p>
              {incomingInterests.map((item) => (
                <div
                  key={item.id}
                  className="rounded-xl border border-white/10 bg-black/20 p-2.5"
                >
                  <p className="text-[10px] font-bold text-white">{item.listing_title}</p>
                  <p className="text-xs text-slate-400">
                    {item.responder_full_name || `Пользователь #${item.responder_id}`}
                  </p>
                  {item.message ? (
                    <p className="mt-1 line-clamp-2 text-[10px] text-slate-500">{item.message}</p>
                  ) : null}
                  <button
                    type="button"
                    disabled={acceptBusyId != null}
                    onClick={() => acceptIncoming(item)}
                    className="mt-2 w-full rounded-lg bg-indigo-600 py-1.5 text-[9px] font-black uppercase text-white hover:bg-indigo-500 disabled:opacity-50"
                  >
                    {acceptBusyId === item.id ? '…' : 'Принять'}
                  </button>
                </div>
              ))}
            </div>
          ) : null}
          {!loadingList && exchanges.length === 0 && incomingInterests.length === 0 ? (
            <p className="px-2 text-xs leading-relaxed text-slate-500">
              Чатов пока нет. Если вы откликнулись на заказ — дождитесь, пока автор примет
              отклик. Если вы автор — примите отклик в{' '}
              <Link to="/deals" className="text-indigo-400 hover:text-indigo-300">
                каталоге
              </Link>{' '}
              (своё объявление) или здесь, когда отклик появится выше.
            </p>
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
              onClick={() => setSelectedId(chat.id)}
              className={`flex w-full items-center space-x-3 rounded-2xl p-4 text-left transition-all ${
                selectedId === chat.id
                  ? 'border border-indigo-500/20 bg-indigo-600/10'
                  : 'border border-transparent hover:bg-white/5'
              }`}
            >
              <div
                className={`flex size-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                  selectedId === chat.id ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                }`}
              >
                {String(chat.name).charAt(0)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex justify-between gap-2">
                  <p
                    className={`truncate text-xs font-bold ${
                      selectedId === chat.id ? 'text-white' : 'text-slate-300'
                    }`}
                  >
                    {chat.name}
                  </p>
                  {chat.time ? (
                    <span className="shrink-0 text-[8px] text-slate-500">{chat.time}</span>
                  ) : null}
                </div>
                {chat.subtitle ? (
                  <p className="mt-0.5 truncate text-[9px] text-slate-600">{chat.subtitle}</p>
                ) : null}
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
              {title.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <h3 className="truncate text-sm font-bold text-white">{title}</h3>
              <div className="flex items-center space-x-2">
                {selected ? (
                  <span className="size-1.5 shrink-0 animate-pulse rounded-full bg-green-500" />
                ) : null}
                <span className="truncate text-[10px] font-bold uppercase tracking-widest text-slate-500">
                  {selected
                    ? (statusLabel[selected.status] ?? selected.status)
                    : 'Выберите сделку слева'}
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
            {hasSelection && selected?.status === 'discussion' ? (
              <button
                type="button"
                disabled={actionBusy}
                onClick={startActiveSwap}
                className="rounded-xl border border-indigo-500/40 bg-indigo-600/20 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-indigo-200 transition hover:bg-indigo-600/40 disabled:opacity-50"
              >
                Начать обмен
              </button>
            ) : null}
            {hasSelection && selected?.status === 'active' ? (
              <button
                type="button"
                disabled={actionBusy || myConfirmed}
                onClick={confirmDone}
                className="rounded-xl bg-indigo-600 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500 disabled:opacity-50"
              >
                {myConfirmed ? 'Вы подтвердили' : 'Подтвердить выполнение'}
              </button>
            ) : null}
          </div>
        </div>

        {error ? (
          <div className="border-b border-red-500/20 bg-red-500/10 px-4 py-2 text-xs text-red-200">
            {error}
          </div>
        ) : null}

        <div className="custom-scrollbar flex-1 space-y-6 overflow-y-auto bg-[radial-gradient(ellipse_at_center,#6366f105,transparent)] p-4 sm:p-6">
          {!hasSelection ? (
            <p className="text-xs text-slate-500">Выберите сделку в списке слева.</p>
          ) : null}
          {hasSelection && selected?.status === 'active' ? (
            <p className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-slate-400">
              {myConfirmed && partnerConfirmed
                ? 'Оба подтвердили — сделка перейдёт в «Завершено».'
                : myConfirmed
                  ? 'Вы подтвердили. Ждём подтверждения партнёра.'
                  : partnerConfirmed
                    ? 'Партнёр подтвердил. Нажмите «Подтвердить выполнение», когда готовы.'
                    : 'Когда обмен выполнен — оба участника нажимают «Подтвердить выполнение».'}
            </p>
          ) : null}
          {hasSelection && selected?.status === 'completed' ? (
            <section className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4">
              <p className="text-[10px] font-black uppercase tracking-widest text-amber-300">
                Отзыв о партнёре
              </p>
              {myReview ? (
                <p className="mt-2 text-sm text-slate-300">
                  Вы оценили сделку на {myReview.rating}/5.
                  {myReview.comment ? ` «${myReview.comment}»` : ''}
                </p>
              ) : (
                <>
                  <p className="mt-1 text-xs text-slate-500">
                    Оцените {selected.partner_full_name || 'партнёра'} после завершённой сделки.
                  </p>
                  <div className="mt-3 flex gap-1">
                    {[1, 2, 3, 4, 5].map((n) => (
                      <button
                        key={n}
                        type="button"
                        onClick={() => setReviewRating(n)}
                        className={`size-9 rounded-lg text-sm font-bold transition ${
                          reviewRating >= n
                            ? 'bg-amber-500 text-slate-950'
                            : 'bg-white/10 text-slate-500 hover:bg-white/20'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    rows={2}
                    placeholder="Комментарий (необязательно)"
                    className="mt-3 w-full resize-none rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-amber-500/50"
                  />
                  {reviewFeedback ? (
                    <p
                      className={`mt-2 text-xs ${reviewFeedback.type === 'ok' ? 'text-green-400' : 'text-red-400'}`}
                    >
                      {reviewFeedback.text}
                    </p>
                  ) : null}
                  <button
                    type="button"
                    disabled={actionBusy}
                    onClick={submitReview}
                    className="mt-3 rounded-xl bg-amber-500 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-slate-950 hover:bg-amber-400 disabled:opacity-50"
                  >
                    {actionBusy ? 'Отправка…' : 'Отправить отзыв'}
                  </button>
                </>
              )}
            </section>
          ) : null}
          {hasSelection && loadingMsg ? (
            <div className="px-1">
              <LoadingHint label="Загрузка сообщений…" />
            </div>
          ) : null}
          {hasSelection && messages.length === 0 && !loadingMsg ? (
            <p className="text-xs text-slate-500">Пока нет сообщений — напишите первым.</p>
          ) : null}
          {hasSelection
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
            : null}
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
              disabled={
                !hasSelection ||
                !selectedId ||
                selected?.status === 'completed' ||
                selected?.status === 'cancelled'
              }
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
              disabled={!hasSelection || !selectedId}
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
