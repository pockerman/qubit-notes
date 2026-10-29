import { useState, type FormEvent } from 'react'
import type { StudyApi } from '../api'
import { KEY_GIVEN, PROVIDER } from '../providers'

type KeyFormProps = {
  api: StudyApi
  provider: string
  onGiven: () => void
  // where the key is being replaced: going back to the one the app has
  onCancel?: () => void
}

/** An admin giving the app a model provider's key, or another in place of the one it was given. */
export function KeyForm({ api, provider, onGiven, onCancel }: KeyFormProps) {
  const [key, setKey] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const label = `${PROVIDER[provider] ?? provider} key`

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
      <label>
        {label}
        <input type="password" autoComplete="off" value={key} onChange={(e) => setKey(e.target.value)} />
      </label>
      <div className="actions">
        <button type="submit" disabled={saving || !key.trim()}>
          {saving ? 'Saving…' : 'Save'}
        </button>
        {onCancel && (
          <button type="button" className="link" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
    </form>
  )
}
