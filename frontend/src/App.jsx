import { Navigate, Route, Routes } from 'react-router-dom'
import RequireAuth from './components/auth/RequireAuth.jsx'
import AppLayout from './components/layout/AppLayout.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import DealsPage from './pages/DealsPage.jsx'
import MatchingPage from './pages/MatchingPage.jsx'
import MessagesPage from './pages/MessagesPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/deals" element={<DealsPage />} />
        <Route path="/matching" element={<MatchingPage />} />
        <Route element={<RequireAuth />}>
          <Route path="/messages" element={<MessagesPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
