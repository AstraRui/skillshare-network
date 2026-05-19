function AdminTokenCard({ token, onTokenChange, error }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-blue-600">Admin panel</p>

      <h1 className="mt-2 text-2xl font-bold text-slate-900">
        Панель администратора
      </h1>

      <p className="mt-2 text-sm text-slate-500">
        Базовая админка для управления пользователями, listings, сделками и чатами.
      </p>

      <div className="mt-4">
        <label className="mb-2 block text-sm font-medium text-slate-700">
          JWT token администратора
        </label>

        <input
          value={token}
          onChange={(event) => onTokenChange(event.target.value)}
          className="w-full rounded-lg border border-slate-300 bg-slate-50 px-4 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          placeholder="Вставь JWT токен без слова Bearer"
        />
      </div>

      {error ? (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
    </div>
  )
}

export default AdminTokenCard
