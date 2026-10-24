import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { AIModel, Me, StudyApi } from '../api'
import { KeyForm } from '../components/PlatformStatus'
import { PROVIDER } from '../providers'
import { href } from '../router'

/** The app's settings: the AI's provider and model, which its admins choose (features/ui_settings.feature). */
export function SettingsPage({ api }: { api: StudyApi }) {
  const [inUse, setInUse] = useState<AIModel | null>(null)
  const [me, setMe] = useState<Me | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.aiModel().then(setInUse, (e: Error) => setError(e.message))
  }, [api])

  useEffect(load, [load])
  useEffect(() => {
    api.me().then(setMe, () => setMe(null))
  }, [api])

  return (
    <section className="settings" aria-labelledby="settings-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'courses' })}>
          ← My courses
        </a>
        <h2 id="settings-title">Settings</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {inUse && (
        <section className="card" aria-labelledby="ai-model-title">
          <h3 id="ai-model-title">AI model</h3>
          <p>
            The AI uses <strong>{inUse.model}</strong> of {PROVIDER[inUse.provider] ?? inUse.provider}.
          </p>
          {me?.admin ? (
            <ModelForm api={api} inUse={inUse} onChosen={setInUse} />
          ) : (
            <p className="note">Only the app's admins can change it.</p>
          )}
          {me?.admin && !inUse.keys[inUse.provider] && <KeyForm api={api} provider={inUse.provider} onGiven={load} />}
        </section>
      )}
    </section>
  )
}

type ModelFormProps = { api: StudyApi; inUse: AIModel; onChosen: (inUse: AIModel) => void }

/** An admin choosing the AI's provider, and its model by name, with the provider's models suggested. */
function ModelForm({ api, inUse, onChosen }: ModelFormProps) {
  const [provider, setProvider] = useState(inUse.provider)
  const [model, setModel] = useState(inUse.model)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null)

  async function choose(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setMessage(null)
    try {
      const chosen = await api.chooseAIModel(provider, model)
      setMessage({ text: `The AI uses ${chosen.model} of ${PROVIDER[chosen.provider]} from now on.` })
      onChosen(chosen)
    } catch (e) {
      setMessage({ text: (e as Error).message, error: true })
    }
    setSaving(false)
  }

  return (
    <form className="model-form" aria-label="Choose the AI model" onSubmit={choose}>
      <label>
        Provider
        <select
          value={provider}
          onChange={(e) => {
            // a provider comes with its own model, which can be changed
            setProvider(e.target.value)
            setModel(inUse.defaults[e.target.value] ?? '')
          }}
        >
          {Object.keys(inUse.defaults).map((p) => (
            <option key={p} value={p}>
              {PROVIDER[p] ?? p}
            </option>
          ))}
        </select>
      </label>
      <label>
        Model
        <input value={model} onChange={(e) => setModel(e.target.value)} list="suggested-models" required />
        <datalist id="suggested-models">
          {(inUse.suggested[provider] ?? []).map((m) => (
            <option key={m} value={m} />
          ))}
        </datalist>
      </label>
      <p className="note">Any of {PROVIDER[provider] ?? provider}'s models, by the name it gives it</p>
      <div className="actions">
        <button type="submit" disabled={saving || !model.trim()}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
      {message && (
        <p role={message.error ? 'alert' : 'status'} className={message.error ? 'error' : 'note'}>
          {message.text}
        </p>
      )}
    </form>
  )
}
