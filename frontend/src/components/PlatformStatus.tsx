import { useCallback, useEffect, useRef, useState } from 'react'
import type { Health, Me, StudyApi } from '../api'
import { KEY_GIVEN } from '../providers'
import { href } from '../router'

/** Whether the platform is working; where it isn't, it opens to say why, in plain words, and sends an admin to
 * Settings for a key the app is missing. */
export function PlatformStatus({ api }: { api: StudyApi }) {
  const [health, setHealth] = useState<Health | null>(null)
  const [me, setMe] = useState<Me | null>(null)
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const status = useRef<HTMLDivElement>(null)

  const check = useCallback(() => {
    api.health().then(setHealth, (e: Error) => setError(e.message))
  }, [api])

  useEffect(check, [check])
  // a key given in Settings may be the one missing
  useEffect(() => {
    window.addEventListener(KEY_GIVEN, check)
    return () => window.removeEventListener(KEY_GIVEN, check)
  }, [check])
  useEffect(() => {
    api.me().then(setMe, () => setMe(null))
  }, [api])

  // closes on a click outside it, or Escape
  useEffect(() => {
    if (!open) return
    const outside = (event: MouseEvent) => {
      if (!status.current?.contains(event.target as Node)) setOpen(false)
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

  if (error)
    return (
      <span role="status" className="badge bad">
        Backend unreachable
      </span>
    )
  if (!health)
    return (
      <span role="status" className="badge">
        Checking the platform…
      </span>
    )
  if (health.status === 'ok')
    return (
      <span role="status" className="badge good">
        Platform connected
      </span>
    )

  const notServing = Object.entries(health.services)
    .filter(([, status]) => status !== 'SERVING')
    .map(([name]) => name)
  return (
    <div className="platform-status" ref={status}>
      <button
        type="button"
        className="badge bad"
        aria-haspopup="dialog"
        aria-expanded={open}
        title={health.error ?? undefined}
        onClick={() => setOpen(!open)}
      >
        <span role="status">Platform degraded{notServing.length > 0 && `: ${notServing.join(', ')}`}</span> ▾
      </button>
      {open && (
        <div className="popover" role="dialog" aria-label="The platform">
          {health.error && <p className="note">{health.error}</p>}
          {health.missing_keys.length > 0 &&
            (me?.admin ? (
              <p>
                The app is missing a key. Head to{' '}
                <a href={href({ page: 'settings', view: 'ai-model' })} onClick={() => setOpen(false)}>
                  Settings
                </a>{' '}
                to give it.
              </p>
            ) : (
              <p>The app is missing a key. Ask an admin of the app to give it.</p>
            ))}
        </div>
      )}
    </div>
  )
}
