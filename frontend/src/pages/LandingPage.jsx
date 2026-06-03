import { ArrowRight, LayoutGrid, Sparkles, MessageSquare, ShieldCheck, Zap } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { Link } from 'react-router-dom'

const features = [
  {
    Icon: LayoutGrid,
    title: 'Объявления',
    desc: 'Публикуй что предлагаешь и что ищешь. Находи партнёров для обмена навыками.',
  },
  {
    Icon: Sparkles,
    title: 'Matching',
    desc: 'Алгоритм строит граф связей и подбирает цепочки обменов, которые не найти вручную.',
  },
  {
    Icon: MessageSquare,
    title: 'Чат',
    desc: 'Встроенный мессенджер для обсуждения деталей прямо внутри сделки.',
  },
  {
    Icon: ShieldCheck,
    title: 'Сделки',
    desc: 'Прозрачный статус каждого обмена: от обсуждения до подтверждения завершения.',
  },
]

function LandingPage() {
  const { openAuthModal } = useAuth()

  return (
    <div className="animate-page space-y-24">
      {/* Hero */}
      <section className="flex flex-col items-center gap-8 pt-8 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-[11px] font-black uppercase tracking-widest text-indigo-400">
          <Zap size={12} className="fill-indigo-400" />
          Обменивайся навыками, а не деньгами
        </div>

        <h1 className="max-w-3xl text-4xl font-black italic leading-tight text-white sm:text-5xl md:text-6xl">
          Твои знания —{' '}
          <span className="bg-gradient-to-r from-indigo-400 to-fuchsia-400 bg-clip-text text-transparent">
            твоя валюта
          </span>
        </h1>

        <p className="max-w-xl text-sm leading-relaxed text-slate-400 sm:text-base">
          SkillShare — платформа для обмена навыками между людьми. Учи Python в обмен на дизайн.
          Помогай с юридическими вопросами в обмен на маркетинг. Без денег.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <button
            type="button"
            onClick={openAuthModal}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
          >
            Начать бесплатно
            <ArrowRight size={16} />
          </button>
          <Link
            to="/deals"
            className="rounded-xl border border-white/10 px-6 py-3 text-sm font-black uppercase tracking-widest text-slate-400 transition hover:bg-white/5 hover:text-white"
          >
            Смотреть объявления
          </Link>
        </div>
      </section>

      {/* Features */}
      <section>
        <h2 className="mb-10 text-center text-xs font-black uppercase tracking-widest text-slate-500">
          Как это работает
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ Icon, title, desc }) => (
            <div
              key={title}
              className="rounded-2xl border border-white/5 bg-slate-900 p-6 transition hover:border-indigo-500/20 hover:bg-white/5"
            >
              <div className="mb-4 flex size-10 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400">
                <Icon size={20} strokeWidth={2} />
              </div>
              <h3 className="mb-2 text-sm font-black text-white">{title}</h3>
              <p className="text-xs leading-relaxed text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="rounded-[32px] border border-white/5 bg-gradient-to-br from-indigo-600/10 to-fuchsia-600/10 p-10 text-center">
        <h2 className="mb-3 text-2xl font-black italic text-white">Готов обменяться навыками?</h2>
        <p className="mb-8 text-sm text-slate-400">
          Зарегистрируйся за 30 секунд и создай первое объявление.
        </p>
        <button
          type="button"
          onClick={openAuthModal}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-8 py-3 text-sm font-black uppercase tracking-widest text-white transition hover:bg-indigo-500"
        >
          Создать аккаунт
          <ArrowRight size={16} />
        </button>
      </section>
    </div>
  )
}

export default LandingPage
