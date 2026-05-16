import { useEffect } from 'react'
import { X, Zap } from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import AuthForm from './AuthForm.jsx'

function AuthModal() {
  const { authModalOpen, closeAuthModal, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated && authModalOpen) {
      closeAuthModal()
    }
  }, [isAuthenticated, authModalOpen, closeAuthModal])

  if (!authModalOpen) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-modal-title"
      className="fixed inset-0 z-[120] flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm"
      onClick={closeAuthModal}
    >
      <div
        className="relative w-full max-w-md rounded-[32px] border border-white/10 bg-slate-900 p-8 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={closeAuthModal}
          className="absolute right-4 top-4 rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
          aria-label="Закрыть"
        >
          <X size={20} />
        </button>

        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-fuchsia-500 p-2">
            <Zap className="size-5 fill-white text-white" strokeWidth={2.5} aria-hidden />
          </div>
          <h2 id="auth-modal-title" className="text-lg font-black uppercase tracking-tight text-white">
            SkillShare
          </h2>
        </div>

        <p className="mb-6 text-sm text-slate-400">
          Войдите или создайте аккаунт, чтобы откликаться на заказы и пользоваться сетью.
        </p>

        <AuthForm onAuthenticated={closeAuthModal} />
      </div>
    </div>
  )
}

export default AuthModal
