import AdminButton from './AdminButton.jsx'
import AdminEmptyState from './AdminEmptyState.jsx'
import AdminSection from './AdminSection.jsx'
import AdminTable from './AdminTable.jsx'

function AdminExchangesTable({ exchanges, disabled, loading, onLoad, onCancelExchange }) {
  return (
    <AdminSection
      title="Сделки"
      actionLabel="Загрузить"
      disabled={disabled}
      loading={loading}
      onAction={onLoad}
    >
      {exchanges.length === 0 ? (
        <AdminEmptyState text="Сделки пока не загружены" />
      ) : (
        <AdminTable columns={['ID', 'Initiator', 'Listing', 'Status', 'Действия']}>
          {exchanges.map((exchange) => (
            <tr key={exchange.id} className="border-b border-slate-100">
              <td className="px-4 py-3">{exchange.id}</td>
              <td className="px-4 py-3">{exchange.initiator_id}</td>
              <td className="px-4 py-3">{exchange.listing_id || '-'}</td>
              <td className="px-4 py-3">{exchange.status}</td>
              <td className="px-4 py-3">
                <AdminButton variant="danger" onClick={() => onCancelExchange(exchange.id)}>
                  Отменить
                </AdminButton>
              </td>
            </tr>
          ))}
        </AdminTable>
      )}
    </AdminSection>
  )
}

export default AdminExchangesTable
