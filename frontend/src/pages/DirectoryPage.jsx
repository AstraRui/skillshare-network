const categories = [
  {
    title: 'Разработка и продукт',
    items: ['Frontend', 'Backend', 'Аналитика', 'Дизайн интерфейсов'],
  },
  {
    title: 'Маркетинг и продажи',
    items: ['Performance', 'SMM', 'B2B продажи', 'Копирайтинг'],
  },
  {
    title: 'Операционный блок',
    items: ['Рекрутинг', 'Юридическое сопровождение', 'Финансы', 'PMO'],
  },
]

function DirectoryPage() {
  return (
    <section>
      <header className="section-header">
        <p className="eyebrow">Каталог навыков</p>
        <h2>Найдите компетенции для обмена</h2>
        <p className="muted">
          Здесь будут отображаться карточки пользователей и фильтры по навыкам.
          Сейчас это демонстрационная структура интерфейса.
        </p>
      </header>

      <div className="card-grid">
        {categories.map((category) => (
          <article key={category.title} className="feature-card">
            <h3>{category.title}</h3>
            <ul className="tag-list">
              {category.items.map((skill) => (
                <li key={skill}>{skill}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  )
}

export default DirectoryPage
