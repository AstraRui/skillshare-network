import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'
import DashboardPage from '../../pages/DashboardPage.jsx'

function HomeRoute() {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) {
    return <Navigate to="/deals" replace />
  }
  return <DashboardPage />
}

export default HomeRoute
