import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'

/** Открывает модалку входа, если в state пришёл флаг openAuth (после редиректа гостя). */
function OpenAuthFromLocation() {
  const location = useLocation()
  const navigate = useNavigate()
  const { openAuthModal } = useAuth()

  useEffect(() => {
    if (!location.state?.openAuth) return
    openAuthModal()
    const rest = { ...location.state }
    delete rest.openAuth
    navigate(
      { pathname: location.pathname, search: location.search },
      {
        replace: true,
        state: Object.keys(rest).length ? rest : null,
      }
    )
  }, [location.pathname, location.search, location.state, navigate, openAuthModal])

  return null
}

export default OpenAuthFromLocation
