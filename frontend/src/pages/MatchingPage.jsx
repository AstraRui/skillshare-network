import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, User } from 'lucide-react'
import { api } from '../api/client.js'
import LoadingHint from '../components/ui/LoadingHint.jsx'
import { matchToGraphNode, radialXY } from '../lib/matchingGraph.js'

const VIEW_W = 800
const VIEW_H = 500
const centerX = VIEW_W / 2
const centerY = VIEW_H / 2
const SPOKE_RADIUS = 172

function MatchingPage() {
  const [graphNodes, setGraphNodes] = useState([])
  const [centerLabel, setCenterLabel] = useState('Вы')
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [needsWantedSkills, setNeedsWantedSkills] = useState(false)
  const [hoveredNode, setHoveredNode] = useState(null)

  const load = useCallback(async () => {
    setLoadError(null)
    setNeedsWantedSkills(false)
    setLoading(true)
    try {
      const [profile, skills, matchesRes] = await Promise.all([
        api.myProfile(),
        api.mySkills(),
        api.matches(),
      ])

      const wantedCount = skills.wanted?.length ?? 0
      if (wantedCount === 0) {
        setNeedsWantedSkills(true)
        setGraphNodes([])
        setCenterLabel(profile.full_name?.trim() || 'Вы')
        return
      }

      setNeedsWantedSkills(false)
      setCenterLabel(profile.full_name?.trim() || 'Вы')
      const nodes = (matchesRes.results ?? []).map(matchToGraphNode)
      setGraphNodes(nodes)
    } catch (e) {
      setLoadError(e.message || 'Не удалось загрузить matching')
      setGraphNodes([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    queueMicrotask(() => {
      void load()
    })
  }, [load])

  const nodes = useMemo(() => {
    const total = graphNodes.length || 1
    return graphNodes.map((m, i) => ({
      ...m,
      ...radialXY(i, total, SPOKE_RADIUS, centerX, centerY),
    }))
  }, [graphNodes])

  const activeNode = useMemo(
    () => nodes.find((m) => m.id === hoveredNode) ?? null,
    [nodes, hoveredNode],
  )

  const nodeStyle = (m) => {
    const leftPct = (m.x / VIEW_W) * 100
    const topPct = (m.y / VIEW_H) * 100
    const scaled = hoveredNode === m.id
    return {
      left: `${leftPct}%`,
      top: `${topPct}%`,
      transform: scaled ? 'translate(-50%, -50%) scale(1.12)' : 'translate(-50%, -50%)',
    }
  }

  return (
    <div className="animate-page space-y-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-2xl font-black italic text-white sm:text-3xl">
            AI CORE <span className="text-indigo-500">VISUALIZER</span>
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Подбор партнёров по навыкам «предлагаю» / «ищу» из вашего профиля.
          </p>
          {loading ? (
            <div className="mt-2">
              <LoadingHint label="Считаем совпадения…" />
            </div>
          ) : null}
          {loadError ? (
            <p className="mt-2 text-xs text-amber-400/90">{loadError}</p>
          ) : null}
        </div>
        {!loading && !loadError ? (
          <span className="inline-flex w-fit rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-[10px] font-bold text-green-400">
            {needsWantedSkills
              ? 'НУЖНЫ НАВЫКИ В ПРОФИЛЕ'
              : `СОВПАДЕНИЙ: ${nodes.length}`}
          </span>
        ) : null}
      </div>

      {needsWantedSkills ? (
        <div className="rounded-[32px] border border-indigo-500/20 bg-indigo-500/5 px-6 py-10 text-center">
          <p className="text-sm text-slate-300">
            Чтобы алгоритм нашёл партнёров, добавьте хотя бы один навык в блок{' '}
            <span className="font-bold text-fuchsia-400">«Я ищу»</span> в профиле.
          </p>
          <Link
            to="/profile"
            className="mt-6 inline-block rounded-xl bg-indigo-600 px-6 py-3 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
          >
            Перейти в профиль
          </Link>
        </div>
      ) : null}

      {!needsWantedSkills && !loading && !loadError && nodes.length === 0 ? (
        <div className="rounded-[32px] border border-white/10 bg-white/5 px-6 py-10 text-center">
          <p className="text-sm text-slate-400">
            Пока нет подходящих партнёров. Добавьте больше навыков или загляните позже — в сети
            появятся новые пользователи.
          </p>
          <Link
            to="/profile"
            className="mt-6 inline-block rounded-xl border border-white/10 px-6 py-3 text-[10px] font-black uppercase tracking-widest text-slate-300 transition hover:bg-white/5"
          >
            Обновить навыки
          </Link>
        </div>
      ) : null}

      {!needsWantedSkills && nodes.length > 0 ? (
        <div className="relative flex min-h-[560px] w-full flex-col items-center justify-center overflow-hidden rounded-[40px] border border-white/5 bg-slate-950 px-4 pb-28 pt-6 shadow-2xl md:px-6 md:pb-32">
          <div className="absolute inset-0 bg-[radial-gradient(#ffffff05_1px,transparent_1px)] bg-[length:30px_30px]" />
          <div className="relative z-0 aspect-[800/500] w-full max-w-5xl">
            <svg
              className="pointer-events-none absolute inset-0 size-full"
              viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
              preserveAspectRatio="xMidYMid meet"
            >
              {nodes.map((m) => (
                <g key={m.id}>
                  <line
                    x1={centerX}
                    y1={centerY}
                    x2={m.x}
                    y2={m.y}
                    stroke={m.type === 'predictive' ? '#d946ef' : '#6366f1'}
                    strokeWidth={hoveredNode === m.id ? '3' : '1'}
                    className={`transition-all duration-500 ${hoveredNode === m.id ? 'opacity-100' : 'opacity-20'}`}
                  />
                  <circle r="3" fill={m.type === 'predictive' ? '#d946ef' : '#6366f1'}>
                    <animateMotion
                      dur="3s"
                      repeatCount="indefinite"
                      path={`M ${m.type === 'incoming' ? m.x : centerX} ${m.type === 'incoming' ? m.y : centerY} L ${m.type === 'incoming' ? centerX : m.x} ${m.type === 'incoming' ? centerY : m.y}`}
                    />
                  </circle>
                </g>
              ))}
            </svg>

            <div className="pointer-events-none absolute left-1/2 top-1/2 z-20 flex size-32 -translate-x-1/2 -translate-y-1/2 items-center justify-center">
              <div className="absolute inset-0 animate-pulse rounded-full bg-indigo-600 opacity-20 blur-3xl" />
              <div className="relative flex size-24 flex-col items-center justify-center rounded-3xl border-2 border-indigo-500 bg-slate-900 px-2 shadow-2xl shadow-indigo-500/20">
                <User className="mb-1 shrink-0 text-indigo-400" size={24} />
                <span className="max-w-full truncate text-center text-[9px] font-black uppercase tracking-tighter text-white">
                  {centerLabel}
                </span>
              </div>
            </div>

            {nodes.map((m) => (
              <div
                key={m.id}
                role="presentation"
                style={nodeStyle(m)}
                className="absolute z-30 cursor-pointer transition-[transform,opacity] duration-300 ease-out will-change-transform"
                onMouseEnter={() => setHoveredNode(m.id)}
                onMouseLeave={() => setHoveredNode(null)}
                onFocus={() => setHoveredNode(m.id)}
                onBlur={() => setHoveredNode(null)}
                tabIndex={0}
              >
                <div
                  className={`flex size-16 flex-col items-center justify-center rounded-2xl border px-1 shadow-lg ${
                    hoveredNode === m.id
                      ? 'border-white bg-indigo-600 shadow-indigo-500/40'
                      : 'border-white/10 bg-slate-900'
                  }`}
                >
                  {m.type === 'predictive' ? (
                    <TrendingUp
                      size={20}
                      className={hoveredNode === m.id ? 'text-white' : 'text-fuchsia-400'}
                    />
                  ) : (
                    <User
                      size={20}
                      className={hoveredNode === m.id ? 'text-white' : 'text-slate-400'}
                    />
                  )}
                  <span
                    className={`mt-1 max-w-full truncate text-center text-[8px] font-bold ${
                      hoveredNode === m.id ? 'text-white' : 'text-slate-500'
                    }`}
                  >
                    {m.matchPercent}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div
            className={`absolute bottom-6 left-1/2 z-40 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 rounded-2xl border border-white/10 bg-slate-900/90 px-6 py-4 shadow-2xl backdrop-blur-xl transition-all duration-500 md:bottom-8 ${
              activeNode ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-4 opacity-0'
            }`}
          >
            {activeNode ? (
              <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-center">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                    {activeNode.skill} · {activeNode.matchPercent}% match
                  </p>
                  <p className="font-bold text-white">{activeNode.name}</p>
                </div>
                <div className="hidden h-8 w-px bg-white/10 sm:block" />
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] font-bold uppercase text-slate-500">Обмен</p>
                  <p className="text-xs text-white">{activeNode.reason}</p>
                  {activeNode.gives !== '—' ? (
                    <p className="mt-1 text-xs text-slate-400">{activeNode.gives}</p>
                  ) : null}
                </div>
                <Link
                  to="/deals"
                  className="rounded-xl bg-indigo-600 px-4 py-2 text-center text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
                >
                  Каталог сделок
                </Link>
              </div>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default MatchingPage
