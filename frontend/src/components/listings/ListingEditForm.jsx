import { useState } from 'react'

function toForm(initial) {
  return {
    title: initial.title ?? '',
    offering_summary: initial.offering_summary ?? '',
    seeking_summary: initial.seeking_summary ?? '',
    description: initial.description ?? '',
  }
}

/**
 * @param {{ initial: { title?: string, offering_summary?: string, seeking_summary?: string, description?: string }, busy?: boolean, submitLabel?: string, onSubmit: (form: ReturnType<typeof toForm>) => void | Promise<void>, onCancel?: () => void }} props
 */
export default function ListingEditForm({
  initial,
  busy = false,
  submitLabel = 'Сохранить',
  onSubmit,
  onCancel,
}) {
  const [form, setForm] = useState(() => toForm(initial))

  const handleSubmit = (e) => {
    e.preventDefault()
    void onSubmit(form)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        required
        value={form.title}
        onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
        placeholder="Заголовок"
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
      />
      <input
        required
        value={form.offering_summary}
        onChange={(e) => setForm((f) => ({ ...f, offering_summary: e.target.value }))}
        placeholder="Что предлагаю"
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
      />
      <input
        required
        value={form.seeking_summary}
        onChange={(e) => setForm((f) => ({ ...f, seeking_summary: e.target.value }))}
        placeholder="Что ищу"
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
      />
      <textarea
        value={form.description}
        onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
        placeholder="Описание (необязательно)"
        rows={3}
        className="w-full resize-none rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
      />
      <div className="flex flex-col gap-2 sm:flex-row">
        <button
          type="submit"
          disabled={busy}
          className="flex-1 rounded-xl bg-indigo-600 px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {busy ? 'Сохранение…' : submitLabel}
        </button>
        {onCancel ? (
          <button
            type="button"
            disabled={busy}
            onClick={onCancel}
            className="rounded-xl border border-white/10 px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-slate-300 hover:bg-white/5 disabled:opacity-50"
          >
            Отмена
          </button>
        ) : null}
      </div>
    </form>
  )
}
