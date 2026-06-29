export default function Toast({ toast }) {
  var borderColor = toast.type === 'success'
    ? 'rgba(34,216,122,0.35)'
    : toast.type === 'error'
    ? 'rgba(255,79,106,0.35)'
    : 'var(--border)'
  var color = toast.type === 'success'
    ? 'var(--green)'
    : toast.type === 'error'
    ? 'var(--red)'
    : 'var(--text)'

  return (
    <div className={'toast' + (toast.show ? ' show' : '')}
      style={{ borderColor: borderColor, color: color }}>
      {toast.msg}
    </div>
  )
}
