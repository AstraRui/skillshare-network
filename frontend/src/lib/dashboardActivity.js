const STATUS_LABELS = {
  discussion: 'Обсуждение',
  active: 'Активный обмен',
  completed: 'Завершено',
  cancelled: 'Отменено',
}

export function formatLogTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const startOfDate = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  const dayDiff = Math.round((startOfToday - startOfDate) / 86400000)
  if (dayDiff === 0) {
    return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }
  if (dayDiff === 1) return 'Вчера'
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
}

/**
 * @param {{ incoming?: object[], exchanges?: object[], matchTotal?: number }} input
 */
export function buildSystemLogs({ incoming = [], exchanges = [], matchTotal = 0 }) {
  const items = []

  for (const interest of incoming) {
    const who = interest.responder_full_name?.trim() || `Пользователь #${interest.responder_id}`
    items.push({
      text: `Новый отклик на «${interest.listing_title}» — ${who}`,
      time: formatLogTime(interest.created_at),
      sortAt: interest.created_at ? new Date(interest.created_at).getTime() : 0,
      type: 'msg',
    })
  }

  for (const ex of exchanges.slice(0, 5)) {
    const title = ex.listing_title ?? `Сделка #${ex.id}`
    const status = STATUS_LABELS[ex.status] ?? ex.status
    items.push({
      text: `Сделка «${title}» — ${status}`,
      time: formatLogTime(ex.created_at),
      sortAt: ex.created_at ? new Date(ex.created_at).getTime() : 0,
      type: ex.status === 'active' ? 'match' : 'system',
    })
  }

  if (matchTotal > 0) {
    items.push({
      text: `Алгоритм нашёл ${matchTotal} совпадени${matchTotal === 1 ? 'е' : matchTotal < 5 ? 'я' : 'й'} по навыкам`,
      time: formatLogTime(new Date().toISOString()),
      sortAt: Date.now(),
      type: 'match',
    })
  }

  return items
    .sort((a, b) => b.sortAt - a.sortAt)
    .slice(0, 8)
    .map(({ text, time, type }) => ({ text, time, type }))
}

export function matchCountLabel(total) {
  if (total === 0) return 'Пока нет совпадений — добавьте навыки «хочу учиться» в профиле.'
  const word = total === 1 ? 'совпадение' : total < 5 ? 'совпадения' : 'совпадений'
  return `Алгоритм нашёл ${total} ${word} по вашим навыкам.`
}

export function networkEfficiencyPercent(matches) {
  const top = matches?.results?.[0]
  if (!top?.score?.final_score) return null
  return Math.min(99, Math.round(top.score.final_score * 100))
}

export function matchingPulseText({ skills, matches }) {
  const wanted = skills?.wanted ?? []
  const top = matches?.results?.[0]
  if (wanted.length === 0) {
    return 'Укажите навыки, которым хотите научиться, в профиле — тогда matching сможет подобрать партнёров.'
  }
  if (!top) {
    return `Вы ищете «${wanted[0].name}» и ещё ${Math.max(0, wanted.length - 1)} навык(ов). Совпадений пока нет — попробуйте расширить список.`
  }
  const partner = top.full_name?.trim() || `Пользователь #${top.user_id}`
  const learn = top.skills_i_get?.[0]?.skill_name ?? wanted[0].name
  const pct = Math.round((top.score?.final_score ?? 0) * 100)
  return `Лучшее совпадение — ${partner}: навык «${learn}», оценка алгоритма ${pct}%.`
}
