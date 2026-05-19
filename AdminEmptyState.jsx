const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  danger: 'bg-red-600 text-white hover:bg-red-700',
  success: 'bg-green-600 text-white hover:bg-green-700',
  dark: 'bg-slate-700 text-white hover:bg-slate-800',
}

function AdminButton({ children, variant = 'primary', disabled = false, onClick }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`rounded-lg px-3 py-1.5 text-xs font-medium disabled:cursor-not-allowed disabled:bg-slate-300 ${
        variants[variant] || variants.primary
      }`}
    >
      {children}
    </button>
  )
}

export default AdminButton
