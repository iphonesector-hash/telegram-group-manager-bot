import { useEffect } from 'react'

export default function Modal({ open, onClose, title, children }) {
  useEffect(function() {
    if (open) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = ''
    return function() { document.body.style.overflow = '' }
  }, [open])

  if (!open) return null

  return (
    <div className="modal-overlay" onClick={function(e) { if (e.target === e.currentTarget) onClose() }}>
      <div className="modal-sheet">
        <div className="modal-handle" />
        {title && <div style={{ fontWeight: 700, fontSize: 17, marginBottom: 18 }}>{title}</div>}
        {children}
      </div>
    </div>
  )
}
