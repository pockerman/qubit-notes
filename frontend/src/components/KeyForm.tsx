import { useState, type FormEvent, type ReactNode } from 'react'
import type { StudyApi } from '../api'
import { KEY_GIVEN } from '../providers'

type KeyFormProps = {
  api: StudyApi
  provider: string
  // the field's name, e.g. "Provider key", and what is said of the key above it
  label: string
  about: ReactNode
  onGiven: () => void
}

/** An admin giving the app a model provider's key, or another in place of the one it was given. */
export function KeyForm({ api, provider, label, about, onGiven }: KeyFormProps) {
  const [key, setKey] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function give(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await api.giveKey(provider, key)
      setKey('')
      window.dispatchEvent(new Event(KEY_GIVEN))
      onGiven()
    } catch (e) {
      setError((e as Error).message)
    }
    setSaving(false)
  }

  return (
    <form className="key-form" aria-label={label} onSubmit={give}>
      <p>{about}</p>
      <label>
        {label}
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
