import { useState } from 'react'

const API_URL = '/api/v1/admin'

function getAuthHeaders(token) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

async function requestAdmin(path, token, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: getAuthHeaders(token),
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(data?.detail || `Ошибка ${response.status}`)
  }

  return data
}

function EmptyState({ text }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center text-sm text-slate-500">
      {text}
    </div>
  )
}

function AdminPanelPage() {
  const [token, setToken] = useState('')
  const [users, setUsers] = useState([])
  const [listings, setListings] = useState([])
  const [exchanges, setExchanges] = useState([])
  const [chats, setChats] = useState([])
  const [messages, setMessages] = useState([])
  const [selectedChatId, setSelectedChatId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState('')

  async function run(actionName, action) {
    setError('')
    setLoading(actionName)

    try {
      await action()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading('')
    }
  }

  async function loadUsers() {
    await run('users', async () => {
      const data = await requestAdmin('/users', token)
      setUsers(data)
    })
  }

  async function setUserBlocked(userId, isDeleted) {
    await run(`user-${userId}`, async () => {
      await requestAdmin(`/users/${userId}/status`, token, {
        method: 'PATCH',
        body: JSON.stringify({ is_deleted: isDeleted }),
      })
      await loadUsers()
    })
  }

  async function loadListings() {
    await run('listings', async () => {
      const data = await requestAdmin('/listings', token)
      setListings(data)
    })
  }

  async function archiveListing(listingId) {
    await run(`listing-${listingId}`, async () => {
      await requestAdmin(`/listings/${listingId}`, token, {
        method: 'DELETE',
      })
      await loadListings()
    })
  }

  async function loadExchanges() {
    await run('exchanges', async () => {
      const data = await requestAdmin('/exchanges', token)
      setExchanges(data)
    })
  }

  async function cancelExchange(exchangeId) {
    await run(`exchange-${exchangeId}`, async () => {
      await requestAdmin(`/exchanges/${exchangeId}`, token, {
        method: 'DELETE',
      })
      await loadExchanges()
    })
  }

  async function loadChats() {
    await run('chats', async () => {
      const data = await requestAdmin('/chats', token)
      setChats(data)
    })
  }

  async function closeChat(chatId) {
    await run(`chat-${chatId}`, async () => {
      await requestAdmin(`/chats/${chatId}`, token, {
        method: 'DELETE',
      })
      await loadChats()
    })
  }

  async function loadMessages(chatId) {
    await run(`messages-${chatId}`, async () => {
      const data = await requestAdmin(`/chats/${chatId}/messages`, token)
      setSelectedChatId(chatId)
      setMessages(data)
    })
  }

  const disabled = !token.trim()

  return (
    <div className="space-y-6 p-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-blue-600">Admin panel</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">
          Панель администратора
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Базовая админка для управления пользователями, listings, сделками и чатами.
        </p>

        <div className="mt-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">
            JWT token администратора
          </label>
          <input
            value={token}
            onChange={(event) => setToken(event.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-slate-50 px-4 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Вставь JWT токен без слова Bearer"
          />
        </div>

        {error ? (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Пользователи</h2>
          <button
            type="button"
            disabled={disabled}
            onClick={loadUsers}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading === 'users' ? 'Загрузка...' : 'Загрузить'}
          </button>
        </div>

        {users.length === 0 ? (
          <EmptyState text="Пользователи пока не загружены" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Имя</th>
                  <th className="px-4 py-3">Роль</th>
                  <th className="px-4 py-3">Blocked</th>
                  <th className="px-4 py-3">Действия</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-slate-100">
                    <td className="px-4 py-3">{user.id}</td>
                    <td className="px-4 py-3">{user.email}</td>
                    <td className="px-4 py-3">{user.full_name || '-'}</td>
                    <td className="px-4 py-3">{user.role}</td>
                    <td className="px-4 py-3">{String(user.is_deleted)}</td>
                    <td className="space-x-2 px-4 py-3">
                      <button
                        type="button"
                        onClick={() => setUserBlocked(user.id, true)}
                        className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Бан
                      </button>
                      <button
                        type="button"
                        onClick={() => setUserBlocked(user.id, false)}
                        className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Разбан
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Listings</h2>
          <button
            type="button"
            disabled={disabled}
            onClick={loadListings}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Загрузить
          </button>
        </div>

        {listings.length === 0 ? (
          <EmptyState text="Listings пока не загружены" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Автор</th>
                  <th className="px-4 py-3">Название</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Действия</th>
                </tr>
              </thead>
              <tbody>
                {listings.map((listing) => (
                  <tr key={listing.id} className="border-b border-slate-100">
                    <td className="px-4 py-3">{listing.id}</td>
                    <td className="px-4 py-3">{listing.author_id}</td>
                    <td className="px-4 py-3">{listing.title}</td>
                    <td className="px-4 py-3">{listing.status}</td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => archiveListing(listing.id)}
                        className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Архивировать
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Сделки</h2>
          <button
            type="button"
            disabled={disabled}
            onClick={loadExchanges}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Загрузить
          </button>
        </div>

        {exchanges.length === 0 ? (
          <EmptyState text="Сделки пока не загружены" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Initiator</th>
                  <th className="px-4 py-3">Listing</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Действия</th>
                </tr>
              </thead>
              <tbody>
                {exchanges.map((exchange) => (
                  <tr key={exchange.id} className="border-b border-slate-100">
                    <td className="px-4 py-3">{exchange.id}</td>
                    <td className="px-4 py-3">{exchange.initiator_id}</td>
                    <td className="px-4 py-3">{exchange.listing_id || '-'}</td>
                    <td className="px-4 py-3">{exchange.status}</td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => cancelExchange(exchange.id)}
                        className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Отменить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Чаты</h2>
          <button
            type="button"
            disabled={disabled}
            onClick={loadChats}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Загрузить
          </button>
        </div>

        {chats.length === 0 ? (
          <EmptyState text="Чаты пока не загружены" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Exchange</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Действия</th>
                </tr>
              </thead>
              <tbody>
                {chats.map((chat) => (
                  <tr key={chat.id} className="border-b border-slate-100">
                    <td className="px-4 py-3">{chat.id}</td>
                    <td className="px-4 py-3">{chat.exchange_id}</td>
                    <td className="px-4 py-3">{chat.status}</td>
                    <td className="space-x-2 px-4 py-3">
                      <button
                        type="button"
                        onClick={() => loadMessages(chat.id)}
                        className="rounded-lg bg-slate-700 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Сообщения
                      </button>
                      <button
                        type="button"
                        onClick={() => closeChat(chat.id)}
                        className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Закрыть
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedChatId ? (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">
            Сообщения чата #{selectedChatId}
          </h2>

          {messages.length === 0 ? (
            <EmptyState text="Сообщений нет" />
          ) : (
            <div className="mt-4 space-y-3">
              {messages.map((message) => (
                <div key={message.id} className="rounded-lg border border-slate-200 p-3">
                  <div className="text-xs text-slate-500">
                    #{message.id} · user {message.sender_id}
                  </div>
                  <div className="mt-1 text-sm text-slate-800">
                    {message.content || 'Без текста'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      ) : null}
    </div>
  )
}

export default AdminPanelPage
