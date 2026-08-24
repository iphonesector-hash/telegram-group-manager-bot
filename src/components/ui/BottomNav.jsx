import { NAV_ITEMS } from '../../utils/mock'
import SectorIcon from './SectorIcon'

export default function BottomNav({ page, onNavigate, isAdmin }) {
  var items = NAV_ITEMS.slice()
  items.splice(2, 0, { key:'assets', label:'دارایی‌ها' })
  if (isAdmin) items.splice(items.length - 1, 0, { key:'admin', label:'مدیریت' })
  return (
    <nav className="bottom-nav" aria-label="نوار دسترسی اصلی">
      {items.map(function(n) {
        return (
          <button
            key={n.key}
            className={'nav-item' + (page === n.key ? ' active' : '')}
            onClick={function() { onNavigate(n.key) }}
            aria-label={n.label}
          >
            <span className="nav-icon"><SectorIcon name={n.key} size={21}/></span>
            <span className="nav-label">{n.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
