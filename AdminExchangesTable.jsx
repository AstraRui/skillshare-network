import AdminButton from './AdminButton.jsx'
import AdminEmptyState from './AdminEmptyState.jsx'
import AdminSection from './AdminSection.jsx'
import AdminTable from './AdminTable.jsx'

function AdminListingsTable({ listings, disabled, loading, onLoad, onArchiveListing }) {
  return (
    <AdminSection
      title="Listings"
      actionLabel="Загрузить"
      disabled={disabled}
      loading={loading}
      onAction={onLoad}
    >
      {listings.length === 0 ? (
        <AdminEmptyState text="Listings пока не загружены" />
      ) : (
        <AdminTable columns={['ID', 'Автор', 'Название', 'Статус', 'Действия']}>
          {listings.map((listing) => (
            <tr key={listing.id} className="border-b border-slate-100">
              <td className="px-4 py-3">{listing.id}</td>
              <td className="px-4 py-3">{listing.author_id}</td>
              <td className="px-4 py-3">{listing.title}</td>
              <td className="px-4 py-3">{listing.status}</td>
              <td className="px-4 py-3">
                <AdminButton variant="danger" onClick={() => onArchiveListing(listing.id)}>
                  Архивировать
                </AdminButton>
              </td>
            </tr>
          ))}
        </AdminTable>
      )}
    </AdminSection>
  )
}

export default AdminListingsTable
