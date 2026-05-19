import AdminButton from './AdminButton.jsx'
import AdminEmptyState from './AdminEmptyState.jsx'
import AdminSection from './AdminSection.jsx'
import AdminTable from './AdminTable.jsx'

function AdminUsersTable({ users, disabled, loading, onLoad, onBlockUser }) {
  return (
    <AdminSection
      title="Пользователи"
      actionLabel="Загрузить"
      disabled={disabled}
      loading={loading}
      onAction={onLoad}
    >
      {users.length === 0 ? (
        <AdminEmptyState text="Пользователи пока не загружены" />
      ) : (
        <AdminTable columns={['ID', 'Email', 'Имя', 'Роль', 'Blocked', 'Действия']}>
          {users.map((user) => (
            <tr key={user.id} className="border-b border-slate-100">
              <td className="px-4 py-3">{user.id}</td>
              <td className="px-4 py-3">{user.email}</td>
              <td className="px-4 py-3">{user.full_name || '-'}</td>
              <td className="px-4 py-3">{user.role}</td>
              <td className="px-4 py-3">{String(user.is_deleted)}</td>
              <td className="space-x-2 px-4 py-3">
                <AdminButton variant="danger" onClick={() => onBlockUser(user.id, true)}>
                  Бан
                </AdminButton>
                <AdminButton variant="success" onClick={() => onBlockUser(user.id, false)}>
                  Разбан
                </AdminButton>
              </td>
            </tr>
          ))}
        </AdminTable>
      )}
    </AdminSection>
  )
}

export default AdminUsersTable
