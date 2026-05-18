import { Navigate, Route, Routes } from 'react-router-dom'
import RequireAuth from './components/auth/RequireAuth.jsx'
import HomeRoute from './components/auth/HomeRoute.jsx'
import AppLayout from './components/layout/AppLayout.jsx'
import DealsPage from './pages/DealsPage.jsx'
import MatchingPage from './pages/MatchingPage.jsx'
import MessagesPage from './pages/MessagesPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomeRoute />} />
        <Route path="/deals" element={<DealsPage />} />
        <Route element={<RequireAuth />}>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/matching" element={<MatchingPage />} />
          <Route path="/messages" element={<MessagesPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/deals" replace />} />
      </Route>
    </Routes>
  )
}

export default App
