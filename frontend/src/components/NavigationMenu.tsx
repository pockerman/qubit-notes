import { useEffect, useRef, useState } from 'react'
import { href } from '../router'

/** The app's menu: My courses, Settings, which opens a submenu of its views, and Sign out. */
export function NavigationMenu({ onSignOut }: { onSignOut: () => void }) {
  const [open, setOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
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

  // opens again with the submenu closed
  function toggle() {
    setOpen(!open)
    setSettingsOpen(false)
  }

  return (
    <div className="navigation-menu" ref={menu}>
      <button type="button" aria-haspopup="menu" aria-expanded={open} onClick={toggle}>
        Menu ▾
      </button>
      {open && (
        <ul className="menu" role="menu" aria-label="Menu">
          <li role="none">
            <a role="menuitem" href={href({ page: 'courses' })} onClick={() => setOpen(false)}>
              My courses
            </a>
          </li>
          <li role="none" className="has-submenu">
            <button
              type="button"
              role="menuitem"
              className="link"
              aria-haspopup="menu"
              aria-expanded={settingsOpen}
              onClick={() => setSettingsOpen(!settingsOpen)}
            >
              Settings
            </button>
            {settingsOpen && (
              <ul className="submenu" role="menu" aria-label="Settings">
                <li role="none">
                  <a role="menuitem" href={href({ page: 'settings', view: 'ai-model' })} onClick={() => setOpen(false)}>
                    AI model
                  </a>
                </li>
                <li role="none">
                  <a role="menuitem" href={href({ page: 'settings', view: 'account' })} onClick={() => setOpen(false)}>
                    Account
                  </a>
                </li>
              </ul>
            )}
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
