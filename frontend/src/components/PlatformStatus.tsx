import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import type { Health, Me, StudyApi } from '../api'
import { PROVIDER } from '../providers'

/** Whether the platform is working; where it isn't, it opens to say why, and lets an admin give the app the keys
 * it is missing. */
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
          {health.missing_keys.map((provider) =>
            me?.admin ? (
              <KeyForm
                key={provider}
                api={api}
                provider={provider}
                onGiven={() => {
                  setOpen(false)
                  check()
                }}
              />
            ) : (
              <p key={provider}>
                The app is missing its {PROVIDER[provider] ?? provider} key. Ask an admin of the app to give it.
              </p>
            ),
          )}
        </div>
      )}
    </div>
  )
}

type KeyFormProps = { api: StudyApi; provider: string; onGiven: () => void }

/** An admin giving the app the key it is missing for a model provider. */
export function KeyForm({ api, provider, onGiven }: KeyFormProps) {
  const [key, setKey] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const name = PROVIDER[provider] ?? provider

  async function give(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await api.giveKey(provider, key)
      onGiven()
    } catch (e) {
      setError((e as Error).message)
      setSaving(false)
    }
  }

  return (
    <form className="key-form" aria-label={`The ${name} key`} onSubmit={give}>
      <p>The app is missing its {name} key.</p>
      <label>
        {name} key
        <input type="password" autoComplete="off" value={key} onChange={(e) => setKey(e.target.value)} />
      </label>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <button type="submit" disabled={saving || !key.trim()}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
      <p className="note">Kept encrypted, and never shown again.</p>
    </form>
  )
}
