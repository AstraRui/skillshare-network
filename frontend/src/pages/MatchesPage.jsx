const flow = [
  {
    step: 'Шаг 1',
    title: 'Сопоставление запросов',
    text: 'Алгоритм сравнивает потребности и доступные навыки участников.',
  },
  {
    step: 'Шаг 2',
    title: 'Построение цепочки',
    text: 'Система ищет непрямые связи, где каждый получает ценность.',
  },
  {
    step: 'Шаг 3',
    title: 'Подтверждение и запуск',
    text: 'Участники согласуют условия и переходят к выполнению обмена.',
  },
]

function MatchesPage() {
  return (
    <section>
      <header className="section-header">
        <p className="eyebrow">Цепочки обмена</p>
        <h2>Как работает matching engine</h2>
        <p className="muted">
          Экран отражает будущий процесс построения multi-hop обменов между
          участниками платформы.
        </p>
      </header>

      <div className="timeline">
        {flow.map((item) => (
          <article key={item.step} className="timeline-item">
            <p className="timeline-step">{item.step}</p>
            <h3>{item.title}</h3>
            <p className="muted">{item.text}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

export default MatchesPage
