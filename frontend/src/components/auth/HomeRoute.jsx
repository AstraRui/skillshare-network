import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'
import DashboardPage from '../../pages/DashboardPage.jsx'
import LandingPage from '../../pages/LandingPage.jsx'

function HomeRoute() {
  const { isAuthenticated, justRegistered, clearJustRegistered } = useAuth()

  if (!isAuthenticated) {
    return <LandingPage />
  }

  // После регистрации сразу перекидываем на профиль для заполнения
  if (justRegistered) {
    clearJustRegistered()
    return <Navigate to="/profile" replace />
  }

  return <DashboardPage />
}

export default HomeRoute
