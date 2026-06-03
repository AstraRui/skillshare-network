import { useCallback, useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { Pencil, X } from 'lucide-react'
import { api } from '../../api/client.js'
import ListingEditForm from '../listings/ListingEditForm.jsx'
import LoadingHint from '../ui/LoadingHint.jsx'

export default function DealListingModal({
  listing,
  isOwnListing,
  interestMessage,
  interestBusy,
  interestFeedback,
  onInterestMessageChange,
  onSubmitInterest,
  onClose,
  onExchangeCreated,
  onListingUpdated,
}) {
  const [pendingInterests, setPendingInterests] = useState([])
  const [loadingInterests, setLoadingInterests] = useState(false)
  const [acceptBusyId, setAcceptBusyId] = useState(null)
  const [localError, setLocalError] = useState(null)
  const [editOpen, setEditOpen] = useState(false)
  const [saveListingBusy, setSaveListingBusy] = useState(false)

  const loadInterests = useCallback(async () => {
    if (!isOwnListing || !listing?.id) return
    setLoadingInterests(true)
    setLocalError(null)
    try {
      const rows = await api.listingInterests(listing.id)
      setPendingInterests(rows)
    } catch (e) {
      setLocalError(e.message)
      setPendingInterests([])
    } finally {
      setLoadingInterests(false)
    }
  }, [isOwnListing, listing])

  useEffect(() => {
    if (!isOwnListing) return
    queueMicrotask(() => {
      void loadInterests()
    })
  }, [isOwnListing, loadInterests])

  const saveListing = async (form) => {
    if (!listing?.id) return
    setSaveListingBusy(true)
    setLocalError(null)
    try {
      const updated = await api.updateListing(listing.id, {
        title: form.title.trim(),
        offering_summary: form.offering_summary.trim(),
        seeking_summary: form.seeking_summary.trim(),
        description: form.description.trim() || null,
      })
      onListingUpdated?.(updated)
      setEditOpen(false)
    } catch (e) {
      setLocalError(e.message)
    } finally {
      setSaveListingBusy(false)
    }
  }

  const acceptInterest = async (responderId) => {
    if (!listing?.id) return
    setAcceptBusyId(responderId)
    setLocalError(null)
    try {
      const exchange = await api.acceptListingInterest(listing.id, responderId)
      onExchangeCreated?.(exchange)
      onClose()
    } catch (e) {
      setLocalError(e.message)
    } finally {
      setAcceptBusyId(null)
    }
  }

  if (!listing) return null

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/90 p-4 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
      aria-labelledby="deal-modal-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md overflow-hidden rounded-[28px] border border-white/10 bg-slate-900 shadow-[0_24px_80px_rgba(0,0,0,0.55)]"
        style={{ maxHeight: 'min(85vh, 640px)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="max-h-[min(85vh,640px)] overflow-y-auto overscroll-contain">
          <header className="sticky top-0 z-10 flex items-start justify-between gap-3 border-b border-white/10 bg-slate-900 px-5 py-4">
            <div className="min-w-0 flex-1 pr-2">
              {isOwnListing ? (
                <span className="mb-2 inline-block rounded-lg bg-indigo-500/20 px-2.5 py-1 text-[9px] font-black uppercase tracking-widest text-indigo-300">
                  Ваше объявление
                </span>
              ) : null}
              <h3
                id="deal-modal-title"
                className="text-lg font-black leading-snug text-white sm:text-xl"
              >
                {listing.role}
              </h3>
              <p className="mt-0.5 text-xs text-slate-500">{listing.user}</p>
            </div>
            <div className="flex shrink-0 gap-1">
              {isOwnListing ? (
                <button
                  type="button"
                  onClick={() => setEditOpen((v) => !v)}
                  className="rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
                  aria-label="Редактировать объявление"
                >
                  <Pencil size={18} />
                </button>
              ) : null}
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
                aria-label="Закрыть"
              >
                <X size={20} />
              </button>
            </div>
          </header>

          <div className="space-y-4 px-5 pb-5 pt-4">
            {isOwnListing && editOpen ? (
              <section className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-4">
                <p className="mb-3 text-[10px] font-black uppercase tracking-widest text-indigo-300">
                  Редактирование
                </p>
                <ListingEditForm
                  key={listing.id}
                  initial={{
                    title: listing.role,
                    offering_summary: listing.offer,
                    seeking_summary: listing.seeking,
                    description: listing.description ?? '',
                  }}
                  busy={saveListingBusy}
                  onSubmit={saveListing}
                  onCancel={() => setEditOpen(false)}
                />
              </section>
            ) : null}
            {localError ? (
              <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-300">
                {localError}
              </p>
            ) : null}

            {!editOpen && listing.description ? (
              <p className="text-sm leading-relaxed text-slate-400">{listing.description}</p>
            ) : null}

            <section className="space-y-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm">
              <div>
                <p className="mb-1 text-[10px] font-black uppercase text-slate-500">Предлагает</p>
                <p className="font-bold leading-snug text-white">{listing.offer}</p>
              </div>
              <div className="h-px bg-white/10" role="presentation" />
              <div>
                <p className="mb-1 text-[10px] font-black uppercase text-slate-500">Ищет</p>
                <p className="font-bold leading-snug text-fuchsia-400">{listing.seeking}</p>
              </div>
            </section>

            {listing.tags?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {listing.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-md border border-white/5 bg-black/40 px-2.5 py-1 font-mono text-[9px] font-bold text-slate-400"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            ) : null}

            {isOwnListing ? (
              <section className="space-y-3 rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-4">
                <p className="text-sm leading-relaxed text-slate-300">
                  Отклик не открывает чат сразу. Примите отклик — тогда появится сделка и переписка
                  в «Сообщениях».
                </p>
                {loadingInterests ? <LoadingHint label="Загрузка откликов…" /> : null}
                {!loadingInterests && pendingInterests.length === 0 ? (
                  <p className="text-xs text-slate-500">Входящих откликов пока нет.</p>
                ) : null}
                {!loadingInterests
                  ? pendingInterests.map((item) => (
                      <div
                        key={item.id}
                        className="rounded-xl border border-white/10 bg-black/20 p-3"
                      >
                        <p className="text-xs font-bold text-white">
                          {item.responder_full_name || `Пользователь #${item.responder_id}`}
                        </p>
                        {item.message ? (
                          <p className="mt-1 text-xs text-slate-400">{item.message}</p>
                        ) : null}
                        <button
                          type="button"
                          disabled={acceptBusyId != null}
                          onClick={() => acceptInterest(item.responder_id)}
                          className="mt-3 w-full rounded-lg bg-indigo-600 py-2 text-[10px] font-black uppercase tracking-widest text-white hover:bg-indigo-500 disabled:opacity-50"
                        >
                          {acceptBusyId === item.responder_id ? 'Принимаем…' : 'Принять отклик'}
                        </button>
                      </div>
                    ))
                  : null}
                <Link
                  to="/messages"
                  onClick={onClose}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2.5 text-[10px] font-black uppercase tracking-widest text-slate-300 transition hover:bg-white/5"
                >
                  Все отклики в сообщениях
                </Link>
              </section>
            ) : (
              <section className="space-y-3 border-t border-white/10 pt-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                  Откликнуться
                </p>
                <textarea
                  value={interestMessage}
                  onChange={(e) => onInterestMessageChange(e.target.value)}
                  rows={3}
                  placeholder="Коротко: чем можете помочь (необязательно)"
                  className="w-full resize-none rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                />
                {interestFeedback ? (
                  <p
                    className={`text-xs ${interestFeedback.type === 'ok' ? 'text-green-400' : 'text-red-400'}`}
                  >
                    {interestFeedback.text}
                  </p>
                ) : null}
                <div className="flex flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    disabled={interestBusy}
                    onClick={onSubmitInterest}
                    className="flex-1 rounded-xl bg-indigo-600 px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-indigo-500 disabled:opacity-50"
                  >
                    {interestBusy ? 'Отправка…' : 'Отправить отклик'}
                  </button>
                  <Link
                    to="/messages"
                    onClick={onClose}
                    className="rounded-xl border border-white/10 px-4 py-2.5 text-center text-[10px] font-black uppercase tracking-widest text-slate-300 transition hover:bg-white/5 sm:flex-1"
                  >
                    Сообщения
                  </Link>
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}
