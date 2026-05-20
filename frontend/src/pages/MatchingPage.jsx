import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, User, X } from 'lucide-react'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import LoadingHint from '../components/ui/LoadingHint.jsx'

const VIEW_W = 800
const VIEW_H = 500
const centerX = VIEW_W / 2
const centerY = VIEW_H / 2
const SPOKE_RADIUS = 172

function radialXY(index, total, r, cx, cy) {
  const angle = -Math.PI / 2 + (index / total) * 2 * Math.PI
  return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }
}

// Преобразуем ответ API в формат для визуализации
function matchToNode(match, index, total) {
  const { x, y } = radialXY(index, total, SPOKE_RADIUS, centerX, centerY)
  const topSkill = match.skills_i_get?.[0]
  return {
    id: match.user_id,
    name: match.full_name ?? `Пользователь #${match.user_id}`,
    skill: topSkill?.skill_name ?? 'Навык',
    score: match.score?.final_score ?? 0,
    skillsIGet: match.skills_i_get ?? [],
    skillsIGive: match.skills_i_give ?? [],
    type: match.score?.s_skills > 0.7 ? 'incoming' : 'predictive',
    x,
    y,
  }
}

function MatchingPage() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [nodes, setNodes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  // hoveredNode — подсветка при наведении
  // selectedNode — зафиксированный выбор по клику
  const [hoveredNode, setHoveredNode] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)

  useEffect(() => {
    if (!isAuthenticated) return
    let cancelled = false
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await api.matches()
        if (!cancelled) {
          const results = data.results ?? []
          setNodes(results.map((m, i) => matchToNode(m, i, results.length)))
        }
      } catch (e) {
        if (!cancelled) setError(e.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [isAuthenticated])

  // Если есть зафиксированный клик — показываем его, иначе hover
  // Панель остаётся пока пользователь не кликнет ещё раз или не нажмёт X
  const activeId = selectedNode ?? hoveredNode
  const panelNode = selectedNode != null
    ? nodes.find((n) => n.id === selectedNode)
    : null
  const activeNode = panelNode ?? (hoveredNode != null ? nodes.find((n) => n.id === hoveredNode) : null)

  const nodeStyle = (n) => ({
    left: `${(n.x / VIEW_W) * 100}%`,
    top: `${(n.y / VIEW_H) * 100}%`,
    transform:
      activeId === n.id
        ? 'translate(-50%, -50%) scale(1.12)'
        : 'translate(-50%, -50%)',
  })

  if (!isAuthenticated) {
    return (
      <div className="animate-page flex min-h-[400px] items-center justify-center rounded-[40px] border border-white/5 bg-slate-950">
        <p className="text-sm text-slate-500">Войдите, чтобы увидеть матчи</p>
      </div>
    )
  }

  return (
    <div className="animate-page space-y-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <h2 className="text-2xl font-black italic text-white sm:text-3xl">
          AI CORE <span className="text-indigo-500">VISUALIZER</span>
        </h2>
        {loading ? (
          <LoadingHint label="Ищем матчи…" />
        ) : (
          <span className="inline-flex w-fit rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-[10px] font-bold text-green-400">
            LIVE: {nodes.length} NODES
          </span>
        )}
      </div>

      {error ? (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-xs text-red-300">
          {error}
        </div>
      ) : null}

      {!loading && nodes.length === 0 && !error ? (
        <div className="flex min-h-[400px] items-center justify-center rounded-[40px] border border-white/5 bg-slate-950">
          <div className="text-center">
            <p className="text-sm font-bold text-slate-400">Матчи не найдены</p>
            <p className="mt-2 text-xs text-slate-600">
              Заполните профиль и добавьте навыки, чтобы алгоритм нашёл подходящих кандидатов.
            </p>
          </div>
        </div>
      ) : (
        <div className="relative flex min-h-[560px] w-full flex-col items-center justify-center overflow-hidden rounded-[40px] border border-white/5 bg-slate-950 px-4 pb-28 pt-6 shadow-2xl md:px-6 md:pb-32">
          <div className="absolute inset-0 bg-[radial-gradient(#ffffff05_1px,transparent_1px)] bg-[length:30px_30px]" />

          <div className="relative z-0 aspect-[800/500] w-full max-w-5xl">
            <svg
              className="pointer-events-none absolute inset-0 size-full"
              viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
              preserveAspectRatio="xMidYMid meet"
            >
              {nodes.map((n) => (
                <g key={n.id}>
                  <line
                    x1={centerX}
                    y1={centerY}
                    x2={n.x}
                    y2={n.y}
                    stroke={n.type === 'predictive' ? '#d946ef' : '#6366f1'}
                    strokeWidth={activeId === n.id ? '3' : '1'}
                    className={`transition-all duration-500 ${activeId === n.id ? 'opacity-100' : 'opacity-20'}`}
                  />
                  <circle r="3" fill={n.type === 'incoming' ? '#6366f1' : '#d946ef'}>
                    <animateMotion
                      dur="3s"
                      repeatCount="indefinite"
                      path={`M ${n.type === 'incoming' ? n.x : centerX} ${n.type === 'incoming' ? n.y : centerY} L ${n.type === 'incoming' ? centerX : n.x} ${n.type === 'incoming' ? centerY : n.y}`}
                    />
                  </circle>
                </g>
              ))}
            </svg>

            {/* Центральный узел */}
            <div className="pointer-events-none absolute left-1/2 top-1/2 z-20 flex size-32 -translate-x-1/2 -translate-y-1/2 items-center justify-center">
              <div className="absolute inset-0 animate-pulse rounded-full bg-indigo-600 opacity-20 blur-3xl" />
              <div className="relative flex size-24 flex-col items-center justify-center rounded-3xl border-2 border-indigo-500 bg-slate-900 shadow-2xl shadow-indigo-500/20">
                <User className="mb-1 text-indigo-400" size={24} />
                <span className="text-[10px] font-black uppercase tracking-tighter text-white">
                  YOU
                </span>
              </div>
            </div>

            {/* Узлы кандидатов */}
            {nodes.map((n) => (
              <div
                key={n.id}
                role="button"
                tabIndex={0}
                style={nodeStyle(n)}
                className="absolute z-30 cursor-pointer transition-[transform,opacity] duration-300 ease-out will-change-transform"
                onMouseEnter={() => setHoveredNode(n.id)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={() => setSelectedNode((prev) => (prev === n.id ? null : n.id))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ')
                    setSelectedNode((prev) => (prev === n.id ? null : n.id))
                }}
              >
                <div
                  className={`flex size-16 items-center justify-center rounded-2xl border shadow-lg transition-colors ${
                    activeId === n.id
                      ? 'border-white bg-indigo-600 shadow-indigo-500/40'
                      : 'border-white/10 bg-slate-900'
                  }`}
                >
                  {n.type === 'predictive' ? (
                    <TrendingUp
                      size={24}
                      className={activeId === n.id ? 'text-white' : 'text-fuchsia-400'}
                    />
                  ) : (
                    <User
                      size={24}
                      className={activeId === n.id ? 'text-white' : 'text-slate-400'}
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Панель кандидата — остаётся пока не закрыть */}
          {activeNode ? (
            <div className="absolute bottom-6 left-1/2 z-40 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 rounded-2xl border border-white/10 bg-slate-900/90 px-6 py-4 shadow-2xl backdrop-blur-xl md:bottom-8">
              <div className="flex flex-wrap items-start gap-4">
                <div className="flex-1">
                  <p className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                    {activeNode.skill}
                  </p>
                  <p className="font-bold text-white">{activeNode.name}</p>
                  <p className="mt-1 text-[10px] text-slate-500">
                    Score: {(activeNode.score * 100).toFixed(0)}%
                  </p>
                  {activeNode.skillsIGet.length > 0 ? (
                    <p className="mt-1 text-[10px] text-slate-400">
                      Получу:{' '}
                      {activeNode.skillsIGet
                        .map((s) => s.skill_name)
                        .join(', ')}
                    </p>
                  ) : null}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => navigate('/messages')}
                    className="rounded-xl bg-indigo-600 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
                  >
                    Написать
                  </button>
                  {selectedNode != null ? (
                    <button
                      type="button"
                      onClick={() => setSelectedNode(null)}
                      className="rounded-xl border border-white/10 p-2 text-slate-400 transition hover:text-white"
                      aria-label="Закрыть"
                    >
                      <X size={14} />
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}

export default MatchingPage
