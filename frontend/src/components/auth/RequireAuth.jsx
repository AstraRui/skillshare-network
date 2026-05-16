import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'

/**
 * Дочерние маршруты только для авторизованных. Гостя отправляем в каталог и открываем модалку входа.
 */
function RequireAuth() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/deals"
        replace
        state={{
          openAuth: true,
          from: location.pathname + location.search,
        }}
      />
    )
  }

  return <Outlet />
}

export default RequireAuth
