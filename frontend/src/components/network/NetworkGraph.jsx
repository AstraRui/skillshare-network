import { getPoint, links, nodes } from './network.config.js'
import './NetworkGraph.css'

function UserGlyph({ className = '' }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="12" cy="8" r="3.2" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M5.8 18c0-3.1 2.8-5 6.2-5s6.2 1.9 6.2 5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  )
}

function NetworkGraph() {
  return (
    <div className="network-card" aria-label="Граф связей пользователей">
      <div className="network-grid-bg" />

      <svg className="network-lines" viewBox="0 0 100 100" preserveAspectRatio="none">
        {links.map((link, index) => {
          const from = getPoint(link.from)
          const to = getPoint(link.to)
          return (
            <line
              key={`${link.from}-${link.to}-${index}`}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              className="network-line"
            />
          )
        })}
      </svg>

      {nodes.map((node) => (
        <div
          key={node.id}
          className={`network-node ${node.type === 'trend' ? 'network-node--trend' : ''}`}
          style={{ left: `${node.x}%`, top: `${node.y}%` }}
        >
          {node.type === 'trend' ? (
            <span className="network-trend-icon">↗</span>
          ) : (
            <UserGlyph className="network-user-icon" />
          )}
        </div>
      ))}

      <div className="network-center">
        <div className="network-center__glow" />
        <div className="network-center__ring" />
        <div className="network-center__node">
          <UserGlyph className="network-user-icon network-user-icon--center" />
          <span className="network-center__label">CORE USER</span>
        </div>
      </div>
    </div>
  )
}

export default NetworkGraph
