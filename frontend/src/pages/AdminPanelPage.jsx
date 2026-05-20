import { useState } from 'react'

import {
  archiveAdminListing,
  cancelAdminExchange,
  closeAdminChat,
  getAdminChatMessages,
  getAdminChats,
  getAdminExchanges,
  getAdminListings,
  getAdminUsers,
  updateAdminUserStatus,
} from '../../admin/adminApi.js'

import AdminUsersTable from '../../admin/AdminUsersTable.jsx'
import AdminListingsTable from '../../admin/AdminListingsTable.jsx'
import AdminExchangesTable from '../../admin/AdminExchangesTable.jsx'
import AdminChatsTable from '../../admin/AdminChatsTable.jsx'
import AdminMessagesList from '../../admin/AdminMessagesList.jsx'
import AdminTokenCard from '../../admin/AdminTokenCard.jsx'
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

  const disabled = !token.trim()

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
      setUsers(await getAdminUsers(token))
    })
  }

  async function blockUser(userId, isDeleted) {
    await run(`user-${userId}`, async () => {
      await updateAdminUserStatus(token, userId, {
        is_deleted: isDeleted,
      })

      await loadUsers()
    })
  }

  async function loadListings() {
    await run('listings', async () => {
      setListings(await getAdminListings(token))
    })
  }

  async function archiveListing(listingId) {
    await run(`listing-${listingId}`, async () => {
      await archiveAdminListing(token, listingId)
      await loadListings()
    })
  }

  async function loadExchanges() {
    await run('exchanges', async () => {
      setExchanges(await getAdminExchanges(token))
    })
  }

  async function cancelExchange(exchangeId) {
    await run(`exchange-${exchangeId}`, async () => {
      await cancelAdminExchange(token, exchangeId)
      await loadExchanges()
    })
  }

  async function loadChats() {
    await run('chats', async () => {
      setChats(await getAdminChats(token))
    })
  }

  async function closeChat(chatId) {
    await run(`chat-${chatId}`, async () => {
      await closeAdminChat(token, chatId)
      await loadChats()
    })
  }

  async function loadMessages(chatId) {
    await run(`messages-${chatId}`, async () => {
      setMessages(await getAdminChatMessages(token, chatId))
      setSelectedChatId(chatId)
    })
  }

  return (
    <div className="space-y-6 p-6">
      <AdminTokenCard
        token={token}
        onTokenChange={setToken}
        error={error}
      />

      <AdminUsersTable
        users={users}
        disabled={disabled}
        loading={loading === 'users'}
        onLoad={loadUsers}
        onBlockUser={blockUser}
      />

      <AdminListingsTable
        listings={listings}
        disabled={disabled}
        loading={loading === 'listings'}
        onLoad={loadListings}
        onArchiveListing={archiveListing}
      />

      <AdminExchangesTable
        exchanges={exchanges}
        disabled={disabled}
        loading={loading === 'exchanges'}
        onLoad={loadExchanges}
        onCancelExchange={cancelExchange}
      />

      <AdminChatsTable
        chats={chats}
        disabled={disabled}
        loading={loading === 'chats'}
        onLoad={loadChats}
        onCloseChat={closeChat}
        onLoadMessages={loadMessages}
      />

      <AdminMessagesList
        selectedChatId={selectedChatId}
        messages={messages}
      />
    </div>
  )
}

export default AdminPanelPage
