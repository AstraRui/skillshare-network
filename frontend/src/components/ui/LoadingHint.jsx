/**
 * Ненавязчивый индикатор загрузки в стиле существующих подсказок (text-slate-500).
 */
function LoadingHint({ label = 'Загрузка…' }) {
  return (
    <p className="flex items-center gap-2 text-xs text-slate-500">
      <span
        className="inline-block size-1.5 animate-pulse rounded-full bg-indigo-400"
        aria-hidden
      />
      {label}
    </p>
  )
}

export default LoadingHint
