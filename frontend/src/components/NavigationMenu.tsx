import { useEffect, useRef, useState } from 'react'
import { href } from '../router'

/** The app's menu: My courses, Settings (not there yet) and Sign out. */
export function NavigationMenu({ onSignOut }: { onSignOut: () => void }) {
  const [open, setOpen] = useState(false)
  const menu = useRef<HTMLDivElement>(null)

  // closes on a click outside it, or Escape
  useEffect(() => {
    if (!open) return
    const outside = (event: MouseEvent) => {
      if (!menu.current?.contains(event.target as Node)) setOpen(false)
    }
    const escape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', outside)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('mousedown', outside)
      document.removeEventListener('keydown', escape)
    }
  }, [open])

  return (
    <div className="navigation-menu" ref={menu}>
      <button type="button" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen(!open)}>
        Menu ▾
      </button>
      {open && (
        <ul className="menu" role="menu" aria-label="Menu">
          <li role="none">
            <a role="menuitem" href={href({ page: 'courses' })} onClick={() => setOpen(false)}>
              My courses
            </a>
          </li>
          <li role="none">
            <button type="button" role="menuitem" className="link" aria-disabled="true" title="Not there yet">
              Settings
            </button>
          </li>
          <li role="none">
            <button
              type="button"
              role="menuitem"
              className="link"
              onClick={() => {
                setOpen(false)
                onSignOut()
              }}
            >
              Sign out
            </button>
          </li>
        </ul>
      )}
    </div>
  )
}
