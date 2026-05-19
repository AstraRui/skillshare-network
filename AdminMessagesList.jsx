import AdminButton from './AdminButton.jsx'
import AdminEmptyState from './AdminEmptyState.jsx'
import AdminSection from './AdminSection.jsx'
import AdminTable from './AdminTable.jsx'

function AdminChatsTable({ chats, disabled, loading, onLoad, onCloseChat, onLoadMessages }) {
  return (
    <AdminSection
      title="Чаты"
      actionLabel="Загрузить"
      disabled={disabled}
      loading={loading}
      onAction={onLoad}
    >
      {chats.length === 0 ? (
        <AdminEmptyState text="Чаты пока не загружены" />
      ) : (
        <AdminTable columns={['ID', 'Exchange', 'Status', 'Действия']}>
          {chats.map((chat) => (
            <tr key={chat.id} className="border-b border-slate-100">
              <td className="px-4 py-3">{chat.id}</td>
              <td className="px-4 py-3">{chat.exchange_id}</td>
              <td className="px-4 py-3">{chat.status}</td>
              <td className="space-x-2 px-4 py-3">
                <AdminButton variant="dark" onClick={() => onLoadMessages(chat.id)}>
                  Сообщения
                </AdminButton>
                <AdminButton variant="danger" onClick={() => onCloseChat(chat.id)}>
                  Закрыть
                </AdminButton>
              </td>
            </tr>
          ))}
        </AdminTable>
      )}
    </AdminSection>
  )
}

export default AdminChatsTable
