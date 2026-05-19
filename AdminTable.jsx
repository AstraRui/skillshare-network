function AdminSection({ title, actionLabel, loading, disabled, onAction, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>

        {actionLabel ? (
          <button
            type="button"
            disabled={disabled}
            onClick={onAction}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? 'Загрузка...' : actionLabel}
          </button>
        ) : null}
      </div>

      {children}
    </section>
  )
}

export default AdminSection
