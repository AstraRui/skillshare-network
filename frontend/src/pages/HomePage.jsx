import { Link } from 'react-router-dom'
import NetworkGraph from '../components/network/NetworkGraph.jsx'
import './HomePage.css'

const stats = [
  { value: '1 200+', label: 'активных специалистов' },
  { value: '320+', label: 'успешных обменов в месяц' },
  { value: '24/7', label: 'поддержка платформы' },
]

function HomePage() {
  return (
    <section className="hero-section">
      <div className="hero-content">
        <p className="eyebrow">B2B + P2P Skill Barter Platform</p>
        <h1>Обменивайтесь навыками и услугами без прямых платежей</h1>
        <p className="lead">
          SkillShare Network помогает находить взаимовыгодные цепочки обмена между
          специалистами и командами, чтобы закрывать задачи быстрее.
        </p>
        <div className="actions">
          <Link to="/directory" className="btn btn--primary">
            Перейти в каталог
          </Link>
          <Link to="/matches" className="btn btn--ghost">
            Посмотреть цепочки
          </Link>
        </div>
      </div>

      <div className="hero-side">
        <NetworkGraph />
        <div className="stat-grid" aria-label="Ключевые метрики платформы">
          {stats.map((item) => (
            <article key={item.label} className="stat-card">
              <p className="stat-value">{item.value}</p>
              <p className="muted">{item.label}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HomePage
