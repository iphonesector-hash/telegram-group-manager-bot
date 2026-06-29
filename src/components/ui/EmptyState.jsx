export default function EmptyState({ icon, title, sub, action, onAction }) {
  return (
    <div className="fade-up" style={{ textAlign: 'center', padding: '48px 20px' }}>
      <div style={{ fontSize: 52, marginBottom: 12 }}>{icon}</div>
      <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>{title}</div>
      {sub && <div style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 20 }}>{sub}</div>}
      {action && (
        <button className="btn btn-ghost btn-sm" onClick={onAction}>{action}</button>
      )}
    </div>
  )
}
