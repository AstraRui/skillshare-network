import { Outlet } from 'react-router-dom'
import Navigation from './Navigation.jsx'

function AppLayout() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-[#020617] font-sans text-slate-200 selection:bg-indigo-500/30">
      <div
        className="pointer-events-none fixed -left-40 -top-40 size-[600px] rounded-full bg-indigo-600/10 blur-[120px]"
        aria-hidden
      />
      <div
        className="pointer-events-none fixed -bottom-40 -right-40 size-[600px] rounded-full bg-fuchsia-600/10 blur-[120px]"
        aria-hidden
      />

      <Navigation />

      <main className="relative z-10 mx-auto max-w-7xl px-4 pb-16 pt-24 md:px-6 md:pb-20 md:pt-32">
        <Outlet />
      </main>

      <footer className="relative z-10 border-t border-white/5 py-5 text-center text-[11px] text-slate-600">
        SkillShare — MVP · API{' '}
        <code className="text-slate-500">/api/v1</code>
      </footer>
    </div>
  )
}

export default AppLayout
