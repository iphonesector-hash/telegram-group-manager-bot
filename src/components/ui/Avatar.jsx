export default function Avatar({ user, size }) {
  var s = size || 48
  var initials = user && user.first_name ? user.first_name[0].toUpperCase() : 'S'
  if (user && user.photo_url) {
    return (
      <img
        src={user.photo_url}
        className="avatar"
        style={{ width: s, height: s }}
        onError={function(e) { e.currentTarget.style.display = 'none' }}
        alt="avatar"
      />
    )
  }
  return (
    <div className="avatar" style={{ width: s, height: s, fontSize: s * 0.38 }}>
      {initials}
    </div>
  )
}
