/** Преобразует результат API matching в узел графа для MatchingPage. */
export function matchToGraphNode(match) {
  const getNames = (match.skills_i_get ?? [])
    .map((s) => s.skill_name)
    .filter(Boolean)
  const giveNames = (match.skills_i_give ?? [])
    .map((s) => s.skill_name)
    .filter(Boolean)

  const score = match.score?.final_score ?? 0
  const primarySkill = getNames[0] ?? giveNames[0] ?? 'Обмен'

  /** Сильные совпадения — fuchsia «predictive», остальные — indigo «incoming». */
  const type = score >= 0.55 ? 'predictive' : 'incoming'

  const name = match.full_name?.trim() || `Пользователь #${match.user_id}`

  return {
    id: String(match.user_id),
    userId: match.user_id,
    name,
    skill: primarySkill,
    type,
    matchPercent: Math.round(score * 100),
    reason:
      getNames.length > 0
        ? `Вам подойдёт: ${getNames.slice(0, 3).join(', ')}${getNames.length > 3 ? '…' : ''}`
        : 'Есть пересечение по навыкам',
    gives:
      giveNames.length > 0
        ? `Вы предложите: ${giveNames.slice(0, 3).join(', ')}${giveNames.length > 3 ? '…' : ''}`
        : '—',
    skillsIGet: getNames,
    skillsIGive: giveNames,
  }
}

export function radialXY(index, total, r, cx, cy) {
  const angle = -Math.PI / 2 + (index / total) * 2 * Math.PI
  return {
    x: cx + r * Math.cos(angle),
    y: cy + r * Math.sin(angle),
  }
}
