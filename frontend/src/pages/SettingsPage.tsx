import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { AIModel, Health, Me, StudyApi } from '../api'
import { KeyForm } from '../components/KeyForm'
import { PROVIDER } from '../providers'
import { href } from '../router'

/** The app's settings: the AI's provider and model, which its admins choose, with the provider's key, and the
 * embedding model's key while the app is missing it (features/ui_settings.feature). */
export function SettingsPage({ api }: { api: StudyApi }) {
  const [inUse, setInUse] = useState<AIModel | null>(null)
  const [me, setMe] = useState<Me | null>(null)
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.aiModel().then(setInUse, (e: Error) => setError(e.message))
    api.health().then(setHealth, () => setHealth(null))
  }, [api])

  useEffect(load, [load])
  useEffect(() => {
    api.me().then(setMe, () => setMe(null))
  }, [api])

  // the keys the app is missing but the AI's provider's: its embedding model's
  const embeddingKeys = (health?.missing_keys ?? []).filter((provider) => provider !== inUse?.provider)

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
          {me?.admin && <ProviderKey api={api} inUse={inUse} onGiven={load} />}
        </section>
      )}
      {inUse && me?.admin && embeddingKeys.length > 0 && (
        <section className="card" aria-labelledby="embedding-model-title">
          <h3 id="embedding-model-title">Embedding model</h3>
          {embeddingKeys.map((provider) => (
            <KeyForm
              key={provider}
              api={api}
              provider={provider}
              label="Embedding model key"
              about={`The app is missing the key of its embedding model, of ${PROVIDER[provider] ?? provider}.`}
              onGiven={load}
            />
          ))}
        </section>
      )}
    </section>
  )
}

type ProviderKeyProps = { api: StudyApi; inUse: AIModel; onGiven: () => void }

/** The key of the AI's provider: given or replaced by an admin, unless the app's settings give it. */
function ProviderKey({ api, inUse, onGiven }: ProviderKeyProps) {
  const name = PROVIDER[inUse.provider] ?? inUse.provider
  if (inUse.in_settings[inUse.provider]) {
    return (
      <div className="key-form" role="group" aria-label="Provider key">
        <p>{name}'s key, the AI's provider: the app's settings give it, so it is changed there.</p>
      </div>
    )
  }
  return (
    <KeyForm
      api={api}
      provider={inUse.provider}
      label="Provider key"
      about={`${name}'s key, the AI's provider: ${
        inUse.keys[inUse.provider] ? 'the app has it. Saving another replaces it.' : 'the app is missing it.'
      }`}
      onGiven={onGiven}
    />
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
