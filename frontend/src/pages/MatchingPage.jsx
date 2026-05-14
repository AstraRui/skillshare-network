import { useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, User } from 'lucide-react'
import { matchingNodes } from '../data/matchingNodes.js'

/** Единая логическая сетка (как в исходном макете): SVG и HTML-узлы в процентах от этого прямоугольника. */
const VIEW_W = 800
const VIEW_H = 500
const centerX = VIEW_W / 2
const centerY = VIEW_H / 2

function MatchingPage() {
  const [hoveredNode, setHoveredNode] = useState(null)

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
        <h2 className="text-2xl font-black italic text-white sm:text-3xl">
          AI CORE <span className="text-indigo-500">VISUALIZER</span>
        </h2>
        <span className="inline-flex w-fit rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-[10px] font-bold text-green-400">
          LIVE: 1,421 NODES
        </span>
      </div>
      <div className="relative flex min-h-[560px] w-full flex-col items-center justify-center overflow-hidden rounded-[40px] border border-white/5 bg-slate-950 px-4 pb-28 pt-6 shadow-2xl md:px-6 md:pb-32">
        <div className="absolute inset-0 bg-[radial-gradient(#ffffff05_1px,transparent_1px)] bg-[length:30px_30px]" />
        {/*
          Важно: линии SVG (viewBox 800×500) и div-узлы (left/top в %) должны жить в ОДНОМ прямоугольнике
          с тем же соотношением сторон — иначе preserveAspectRatio даёт «поля» и линии не бьют в центры квадратов.
        */}
        <div className="relative z-0 aspect-[800/500] w-full max-w-5xl">
          <svg
            className="pointer-events-none absolute inset-0 size-full"
            viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
            preserveAspectRatio="xMidYMid meet"
          >
            {matchingNodes.map((m) => (
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
                <circle r="3" fill={m.type === 'incoming' ? '#6366f1' : '#d946ef'}>
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
            <div className="relative flex size-24 flex-col items-center justify-center rounded-3xl border-2 border-indigo-500 bg-slate-900 shadow-2xl shadow-indigo-500/20">
              <User className="mb-1 text-indigo-400" size={24} />
              <span className="text-[10px] font-black uppercase tracking-tighter text-white">
                CORE USER
              </span>
            </div>
          </div>
          {matchingNodes.map((m) => (
            <div
              key={m.id}
              role="presentation"
              style={nodeStyle(m)}
              className="absolute z-30 cursor-pointer transition-[transform,opacity] duration-300 ease-out will-change-transform"
              onMouseEnter={() => setHoveredNode(m.id)}
              onMouseLeave={() => setHoveredNode(null)}
            >
              <div
                className={`flex size-16 items-center justify-center rounded-2xl border shadow-lg ${
                  hoveredNode === m.id
                    ? 'border-white bg-indigo-600 shadow-indigo-500/40'
                    : 'border-white/10 bg-slate-900'
                }`}
              >
                {m.type === 'predictive' ? (
                  <TrendingUp
                    size={24}
                    className={hoveredNode === m.id ? 'text-white' : 'text-fuchsia-400'}
                  />
                ) : (
                  <User size={24} className={hoveredNode === m.id ? 'text-white' : 'text-slate-400'} />
                )}
              </div>
            </div>
          ))}
        </div>
        <div
          className={`absolute bottom-6 left-1/2 z-40 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 rounded-2xl border border-white/10 bg-slate-900/90 px-6 py-4 shadow-2xl backdrop-blur-xl transition-all duration-500 md:bottom-8 ${
            hoveredNode ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-4 opacity-0'
          }`}
        >
          {hoveredNode ? (
            <div className="flex flex-wrap items-center gap-4 sm:space-x-6">
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                  {matchingNodes.find((m) => m.id === hoveredNode)?.skill}
                </p>
                <p className="font-bold text-white">
                  {matchingNodes.find((m) => m.id === hoveredNode)?.name}
                </p>
              </div>
              <div className="hidden h-8 w-px bg-white/10 sm:block" />
              <div>
                <p className="text-[10px] font-bold uppercase text-slate-500">Отношение</p>
                <p className="text-xs text-white">
                  {matchingNodes.find((m) => m.id === hoveredNode)?.reason}
                </p>
              </div>
              <Link
                to="/messages"
                className="rounded-xl bg-indigo-600 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
              >
                Открыть чат
              </Link>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export default MatchingPage
