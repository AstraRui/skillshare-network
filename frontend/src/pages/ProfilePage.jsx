import { useCallback, useEffect, useState } from 'react'
import {
  Award,
  CheckCircle2,
  Copy,
  LogOut,
  PlusCircle,
  X,
  Zap,
} from 'lucide-react'
import { api } from '../api/client.js'
import ListingEditForm from '../components/listings/ListingEditForm.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { initialsFromName } from '../lib/userDisplay.js'

function maskToken(token) {
  if (!token || token.length < 16) return '—'
  return `${token.slice(0, 12)}…${token.slice(-6)}`
}

function userLevel(exchangesCount) {
  if (exchangesCount >= 10) return 'PRO'
  if (exchangesCount >= 3) return 'ACTIVE'
  return 'NEW'
}

function ProfilePage() {
  const { userId, email, token, logout } = useAuth()
  const [profile, setProfile] = useState(null)
  const [skills, setSkills] = useState({ offered: [], wanted: [] })
  const [myListings, setMyListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionError, setActionError] = useState(null)
  const [editOpen, setEditOpen] = useState(false)
  const [editName, setEditName] = useState('')
  const [addSkillOpen, setAddSkillOpen] = useState(null)
  const [newSkillName, setNewSkillName] = useState('')
  const [listingOpen, setListingOpen] = useState(false)
  const [editingListingId, setEditingListingId] = useState(null)
  const [listingSaveBusy, setListingSaveBusy] = useState(false)
  const [listingForm, setListingForm] = useState({
    title: '',
    offering_summary: '',
    seeking_summary: '',
    description: '',
  })
  const [tokenCopied, setTokenCopied] = useState(false)

  const reload = useCallback(async () => {
    if (!userId) return
    setError(null)
    try {
      const [prof, sk, list] = await Promise.all([
        api.myProfile(),
        api.mySkills(),
        api.listings({ author_id: userId }),
      ])
      setProfile(prof)
      setSkills(sk)
      setMyListings(list)
    } catch (err) {
      setError(err.message || 'Не удалось загрузить профиль')
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    if (!userId) return
    let cancelled = false
    queueMicrotask(() => {
      if (cancelled) return
      setLoading(true)
      void reload()
    })
    return () => {
      cancelled = true
    }
  }, [userId, reload])

  const displayName = profile?.full_name?.trim() || email?.split('@')[0] || 'Пользователь'
  const initials = initialsFromName(profile?.full_name, email)

  const handleSaveName = async (e) => {
    e.preventDefault()
    setActionError(null)
    try {
      const updated = await api.updateMyProfile({ full_name: editName.trim() || null })
      setProfile(updated)
      setEditOpen(false)
    } catch (err) {
      setActionError(err.message || 'Не удалось сохранить')
    }
  }

  const handleAddSkill = async (e) => {
    e.preventDefault()
    const name = newSkillName.trim()
    if (!name) return
    setActionError(null)
    try {
      if (addSkillOpen === 'offered') {
        await api.addOfferedSkill({ name })
      } else {
        await api.addWantedSkill({ name })
      }
      setNewSkillName('')
      setAddSkillOpen(null)
      const sk = await api.mySkills()
      setSkills(sk)
    } catch (err) {
      setActionError(err.message || 'Не удалось добавить навык')
    }
  }

  const handleRemoveSkill = async (kind, skillId) => {
    setActionError(null)
    try {
      if (kind === 'offered') await api.removeOfferedSkill(skillId)
      else await api.removeWantedSkill(skillId)
      const sk = await api.mySkills()
      setSkills(sk)
    } catch (err) {
      setActionError(err.message || 'Не удалось удалить навык')
    }
  }

  const handleUpdateListing = async (listingId, form) => {
    setActionError(null)
    setListingSaveBusy(true)
    try {
      await api.updateListing(listingId, {
        title: form.title.trim(),
        offering_summary: form.offering_summary.trim(),
        seeking_summary: form.seeking_summary.trim(),
        description: form.description.trim() || null,
      })
      setEditingListingId(null)
      const [prof, list] = await Promise.all([api.myProfile(), api.listings({ author_id: userId })])
      setProfile(prof)
      setMyListings(list)
    } catch (err) {
      setActionError(err.message || 'Не удалось сохранить объявление')
    } finally {
      setListingSaveBusy(false)
    }
  }

  const handleCreateListing = async (e) => {
    e.preventDefault()
    setActionError(null)
    try {
      await api.createListing({
        title: listingForm.title.trim(),
        offering_summary: listingForm.offering_summary.trim(),
        seeking_summary: listingForm.seeking_summary.trim(),
        description: listingForm.description.trim() || null,
        status: 'published',
      })
      setListingForm({ title: '', offering_summary: '', seeking_summary: '', description: '' })
      setListingOpen(false)
      const [prof, list] = await Promise.all([api.myProfile(), api.listings({ author_id: userId })])
      setProfile(prof)
      setMyListings(list)
    } catch (err) {
      setActionError(err.message || 'Не удалось создать объявление')
    }
  }

  const handleCopyToken = async () => {
    if (!token) return
    try {
      await navigator.clipboard.writeText(token)
      setTokenCopied(true)
      setTimeout(() => setTokenCopied(false), 2000)
    } catch {
      setActionError('Не удалось скопировать токен')
    }
  }

  if (loading) {
    return (
      <p className="py-16 text-center text-sm text-slate-400">Загрузка профиля…</p>
    )
  }

  if (error) {
    return (
      <p className="py-16 text-center text-sm text-red-400">{error}</p>
    )
  }

  return (
    <div className="animate-page grid grid-cols-1 gap-8 lg:grid-cols-4">
      <div className="space-y-6 lg:col-span-1">
        <div className="rounded-[40px] border border-white/5 bg-slate-900 p-6 text-center">
          <h3 className="mb-4 text-left text-sm font-black uppercase tracking-widest text-white">
            Аккаунт
          </h3>
          <div className="space-y-3 text-left text-sm text-slate-300">
            <p>
              <span className="text-slate-500">Сессия:</span> {email}
            </p>
            <button
              type="button"
              onClick={logout}
              className="w-full rounded-xl border border-white/10 bg-white/5 py-2 text-xs font-bold text-white transition hover:bg-white/10"
            >
              Выйти из аккаунта
            </button>
          </div>
        </div>

        <div className="group relative overflow-hidden rounded-[40px] border border-white/5 bg-slate-900 p-8 text-center">
          <div className="absolute left-0 top-0 h-1 w-full bg-gradient-to-r from-indigo-500 to-fuchsia-500" />
          <div className="mx-auto mb-6 flex size-24 rotate-3 items-center justify-center rounded-[32px] bg-indigo-600 text-3xl font-black text-white shadow-2xl transition-transform group-hover:rotate-0">
            {initials}
          </div>
          <h3 className="text-xl font-black italic text-white">{displayName}</h3>
          <p className="mt-1 text-xs font-bold uppercase tracking-widest text-slate-500">
            {email}
          </p>
          <div className="mt-8 space-y-4 border-t border-white/5 pt-8">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-400">Репутация</span>
              <span className="font-black text-indigo-400">
                {profile?.rating > 0 ? `${profile.rating.toFixed(2)} ★` : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-400">Сделок</span>
              <span className="font-black text-white">{profile?.exchanges_count ?? 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-400">Уровень</span>
              <span className="font-black uppercase text-fuchsia-400">
                {userLevel(profile?.exchanges_count ?? 0)}
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              setEditName(profile?.full_name || '')
              setEditOpen(true)
              setActionError(null)
            }}
            className="mt-8 w-full rounded-2xl border border-white/10 bg-white/5 py-3 text-[10px] font-black uppercase tracking-widest text-white transition hover:bg-white/10"
          >
            Редактировать
          </button>
        </div>

        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center justify-center space-x-3 rounded-[32px] border border-white/5 bg-slate-900 p-4 text-red-400 transition hover:bg-red-500/10"
        >
          <LogOut size={16} />
          <span className="text-xs font-bold">Выйти</span>
        </button>
      </div>

      <div className="space-y-8 lg:col-span-3">
        {actionError ? (
          <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-xs text-red-300">
            {actionError}
          </p>
        ) : null}

        <div className="rounded-[40px] border border-white/5 bg-slate-900 p-8">
          <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h3 className="text-2xl font-black uppercase italic text-white">Навыки</h3>
              <p className="mt-2 text-xs font-medium text-slate-500">
                Обновите навыки — алгоритм matching использует их для подбора партнёров.
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setAddSkillOpen(addSkillOpen ? null : 'offered')
                setNewSkillName('')
                setActionError(null)
              }}
              className="rounded-xl bg-indigo-500 p-2 text-white transition hover:bg-indigo-400"
              aria-label="Добавить навык"
            >
              <PlusCircle size={20} />
            </button>
          </div>

          {addSkillOpen ? (
            <form
              onSubmit={handleAddSkill}
              className="mb-6 flex flex-col gap-3 rounded-2xl border border-indigo-500/30 bg-indigo-500/5 p-4 sm:flex-row sm:items-end"
            >
              <label className="flex-1 text-left text-xs text-slate-400">
                Название навыка
                <input
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                  placeholder="Например, Python"
                  className="mt-1 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                  required
                  minLength={2}
                />
              </label>
              <label className="text-left text-xs text-slate-400">
                Список
                <select
                  value={addSkillOpen}
                  onChange={(e) => setAddSkillOpen(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-sm text-white"
                >
                  <option value="offered">Я предлагаю</option>
                  <option value="wanted">Я ищу</option>
                </select>
              </label>
              <button
                type="submit"
                className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-black uppercase text-white hover:bg-indigo-500"
              >
                Добавить
              </button>
              <button
                type="button"
                onClick={() => setAddSkillOpen(null)}
                className="rounded-xl border border-white/10 px-4 py-2 text-xs text-slate-400"
              >
                Отмена
              </button>
            </form>
          ) : null}

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            <div className="space-y-4">
              <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400">
                Я предлагаю
              </h4>
              {skills.offered.length === 0 ? (
                <p className="text-xs text-slate-500">Пока пусто — добавьте навык кнопкой «+»</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {skills.offered.map((s) => (
                    <span
                      key={s.skill_id}
                      className="flex items-center space-x-2 rounded-xl border border-indigo-500/20 bg-indigo-500/10 px-4 py-2 text-xs font-bold text-white"
                    >
                      <span>{s.name}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill('offered', s.skill_id)}
                        className="text-slate-500 hover:text-white"
                        aria-label={`Удалить ${s.name}`}
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="space-y-4">
              <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-fuchsia-400">
                Я ищу
              </h4>
              {skills.wanted.length === 0 ? (
                <p className="text-xs text-slate-500">Пока пусто</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {skills.wanted.map((s) => (
                    <span
                      key={s.skill_id}
                      className="flex items-center space-x-2 rounded-xl border border-fuchsia-500/20 bg-fuchsia-500/10 px-4 py-2 text-xs font-bold text-white"
                    >
                      <span>{s.name}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill('wanted', s.skill_id)}
                        className="text-slate-500 hover:text-white"
                        aria-label={`Удалить ${s.name}`}
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="rounded-[40px] border border-white/5 bg-slate-900 p-8">
          <div className="mb-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h3 className="text-lg font-black uppercase italic text-white">Мои объявления</h3>
              <p className="mt-1 text-xs text-slate-500">
                Опубликовано: {profile?.listings_count ?? 0}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setListingOpen((v) => !v)}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-[10px] font-black uppercase text-white hover:bg-white/10"
            >
              {listingOpen ? 'Скрыть форму' : 'Создать объявление'}
            </button>
          </div>

          {listingOpen ? (
            <form onSubmit={handleCreateListing} className="mb-6 space-y-3 text-left">
              <input
                required
                value={listingForm.title}
                onChange={(e) => setListingForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="Заголовок"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
              />
              <input
                required
                value={listingForm.offering_summary}
                onChange={(e) =>
                  setListingForm((f) => ({ ...f, offering_summary: e.target.value }))
                }
                placeholder="Что предлагаю"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
              />
              <input
                required
                value={listingForm.seeking_summary}
                onChange={(e) =>
                  setListingForm((f) => ({ ...f, seeking_summary: e.target.value }))
                }
                placeholder="Что ищу"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
              />
              <textarea
                value={listingForm.description}
                onChange={(e) =>
                  setListingForm((f) => ({ ...f, description: e.target.value }))
                }
                placeholder="Описание (необязательно)"
                rows={3}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-black uppercase text-white hover:bg-indigo-500"
              >
                Опубликовать
              </button>
            </form>
          ) : null}

          {myListings.length === 0 ? (
            <p className="text-xs text-slate-500">Объявлений пока нет</p>
          ) : (
            <ul className="space-y-3 text-left">
              {myListings.map((l) => (
                <li
                  key={l.id}
                  className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-bold text-white">{l.title}</span>
                    <button
                      type="button"
                      onClick={() =>
                        setEditingListingId((prev) => (prev === l.id ? null : l.id))
                      }
                      className="shrink-0 text-[10px] font-black uppercase text-indigo-400 hover:text-indigo-300"
                    >
                      {editingListingId === l.id ? 'Закрыть' : 'Изменить'}
                    </button>
                  </div>
                  {editingListingId === l.id ? (
                    <div className="mt-3">
                      <ListingEditForm
                        key={l.id}
                        initial={{
                          title: l.title,
                          offering_summary: l.offering_summary,
                          seeking_summary: l.seeking_summary,
                          description: l.description ?? '',
                        }}
                        busy={listingSaveBusy}
                        onSubmit={(form) => handleUpdateListing(l.id, form)}
                        onCancel={() => setEditingListingId(null)}
                      />
                    </div>
                  ) : (
                    <p className="mt-1">
                      {l.offering_summary} → {l.seeking_summary}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
          <div className="rounded-[40px] border border-white/5 bg-slate-900 p-8">
            <h3 className="mb-6 text-lg font-black uppercase italic text-white">Доверие</h3>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-lg bg-green-500/10 p-2 text-green-400">
                    <CheckCircle2 size={16} />
                  </div>
                  <span className="text-sm font-bold text-slate-300">Email подтверждён</span>
                </div>
                <span className="text-[10px] font-black text-green-500">ДА</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-400">
                    <Award size={16} />
                  </div>
                  <span className="text-sm font-bold text-slate-300">Рейтинг</span>
                </div>
                <span className="text-[10px] font-black text-white">
                  {profile?.rating > 0
                    ? `${Math.round(profile.rating * 20)} / 100`
                    : 'Нет отзывов'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="rounded-lg bg-amber-500/10 p-2 text-amber-400">
                    <Zap size={16} />
                  </div>
                  <span className="text-sm font-bold text-slate-300">Сделки</span>
                </div>
                <span className="text-[10px] font-black text-white">
                  {profile?.exchanges_count ?? 0}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-col justify-between rounded-[40px] border border-white/10 bg-gradient-to-br from-indigo-900/40 to-fuchsia-900/40 p-8">
            <div>
              <h3 className="mb-4 text-left text-xl font-black uppercase italic leading-tight text-white">
                Токен доступа
              </h3>
              <p className="text-left text-xs text-slate-400">
                JWT для запросов к API (заголовок Authorization в будущем; сейчас — X-User-Id).
              </p>
            </div>
            <div className="mt-6 flex items-center space-x-2 rounded-2xl border border-white/5 bg-black/40 p-3">
              <code className="flex-1 truncate font-mono text-[10px] text-indigo-300">
                {maskToken(token)}
              </code>
              <button
                type="button"
                onClick={handleCopyToken}
                className="p-1 text-slate-500 transition hover:text-white"
                aria-label="Скопировать токен"
              >
                <Copy size={14} />
              </button>
            </div>
            {tokenCopied ? (
              <p className="mt-2 text-left text-[10px] text-green-400">Скопировано</p>
            ) : null}
          </div>
        </div>
      </div>

      {editOpen ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-profile-title"
        >
          <form
            onSubmit={handleSaveName}
            className="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900 p-6"
          >
            <h2 id="edit-profile-title" className="mb-4 text-lg font-black text-white">
              Редактировать профиль
            </h2>
            <label className="block text-left text-xs text-slate-400">
              Имя
              <input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="mt-1 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                placeholder="Как вас показывать в сети"
              />
            </label>
            <div className="mt-6 flex gap-2">
              <button
                type="submit"
                className="flex-1 rounded-xl bg-indigo-600 py-2 text-xs font-black uppercase text-white"
              >
                Сохранить
              </button>
              <button
                type="button"
                onClick={() => setEditOpen(false)}
                className="flex-1 rounded-xl border border-white/10 py-2 text-xs text-slate-400"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  )
}

export default ProfilePage
