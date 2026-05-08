import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Главная' },
  { to: '/directory', label: 'Каталог навыков' },
  { to: '/matches', label: 'Цепочки обмена' },
]

function AppLayout() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="container nav-wrap">
          <NavLink to="/" className="brand">
            SkillShare Network
          </NavLink>
          <nav className="site-nav" aria-label="Главная навигация">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-link${isActive ? ' nav-link--active' : ''}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="page-main">
        <div className="container">
          <Outlet />
        </div>
      </main>

      <footer className="site-footer">
        <div className="container footer-content">
          <p>SkillShare Network - barter marketplace for skills and services</p>
          <p className="muted">MVP frontend scaffold ready for API integration</p>
        </div>
      </footer>
    </div>
  )
}

export default AppLayout
