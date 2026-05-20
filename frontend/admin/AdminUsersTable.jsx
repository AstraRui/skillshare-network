function AdminUsersTable({ users = [], onLoad }) {
  return (
    <div>
      <button onClick={onLoad}>
        Load users
      </button>

      <table>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default AdminUsersTable
