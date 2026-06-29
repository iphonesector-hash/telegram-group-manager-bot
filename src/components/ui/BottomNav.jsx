import { NAV_ITEMS } from '../../utils/mock'

export default function BottomNav({ page, onNavigate }) {
  return (
    <nav className="bottom-nav">
      {NAV_ITEMS.map(function(n) {
        return (
          <button
            key={n.key}
            className={'nav-item' + (page === n.key ? ' active' : '')}
            onClick={function() { onNavigate(n.key) }}
          >
            <span className="nav-icon">{n.icon}</span>
            <span className="nav-label">{n.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
