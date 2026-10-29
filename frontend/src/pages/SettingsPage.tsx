import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { AIModel, Health, KeyState, Me, StudyApi } from '../api'
import { KeyForm } from '../components/KeyForm'
import { KEY_GIVEN, PROVIDER } from '../providers'
import { href } from '../router'

/** The app's settings: the AI's provider and model, which its admins choose, and the model providers' keys, which
 * they give, replace and remove (features/ui_settings.feature). */
export function SettingsPage({ api }: { api: StudyApi }) {
  const [inUse, setInUse] = useState<AIModel | null>(null)
  const [me, setMe] = useState<Me | null>(null)
  const [health, setHealth] = useState<Health | null>(null)
  const [keys, setKeys] = useState<KeyState[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.aiModel().then(setInUse, (e: Error) => setError(e.message))
    api.health().then(setHealth, () => setHealth(null))
    api.keys().then(setKeys, () => setKeys(null))
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
          {keys && !keys.some((k) => k.provider === inUse.provider && k.given) && (
            <p className="warning">
              The app has no {PROVIDER[inUse.provider] ?? inUse.provider} key yet
              {me?.admin ? ': give it under Keys, below.' : ': ask an admin of the app to give it.'}
            </p>
          )}
        </section>
      )}
      {inUse && keys && me?.admin && (
        <ProviderKeys api={api} keys={keys} missing={health?.missing_keys ?? []} onChanged={load} />
      )}
    </section>
  )
}

type ProviderKeysProps = { api: StudyApi; keys: KeyState[]; missing: string[]; onChanged: () => void }

/** The model providers' keys: whether the app has each, and an admin giving, replacing or removing it. A key the
 * app's settings give is used rather than one given, so it is neither replaced nor removed here. The AI's providers
 * are always listed; the embedding model's, Voyage AI, once the app needs or has its key. */
function ProviderKeys({ api, keys, missing, onChanged }: ProviderKeysProps) {
  const [replacing, setReplacing] = useState<string | null>(null)
  const [removing, setRemoving] = useState<string | null>(null)
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null)
  const listed = keys.filter((k) => k.provider !== 'voyage' || k.given || missing.includes('voyage'))

  function given(provider: string) {
    setReplacing(null)
    setMessage({ text: `The ${PROVIDER[provider] ?? provider} key is saved.` })
    onChanged()
  }

  async function remove(provider: string) {
    try {
      await api.removeKey(provider)
      setMessage({ text: `The ${PROVIDER[provider] ?? provider} key is removed.` })
      window.dispatchEvent(new Event(KEY_GIVEN))
      onChanged()
    } catch (e) {
      setMessage({ text: (e as Error).message, error: true })
    }
    setRemoving(null)
  }

  return (
    <section className="card" aria-labelledby="keys-title">
      <h3 id="keys-title">Keys</h3>
      <p className="note">The model providers' keys, kept encrypted, and never shown again once saved.</p>
      {message && (
        <p role={message.error ? 'alert' : 'status'} className={message.error ? 'error' : 'saved'}>
          {message.text}
        </p>
      )}
      <ul className="provider-keys" aria-label="Keys">
        {listed.map(({ provider, given: has, in_settings }) => {
          const name = PROVIDER[provider] ?? provider
          return (
            <li key={provider} aria-label={`${name} key`}>
              <div className="provider-key">
                <strong>{name}</strong>
                {provider === 'voyage' && <span className="note">the embedding model</span>}
                {in_settings ? (
                  <span className="badge good">Given by the app's settings</span>
                ) : has ? (
                  <span className="badge good">Saved</span>
                ) : (
                  <span className="badge bad">No key</span>
                )}
                {has && !in_settings && replacing !== provider && removing !== provider && (
                  <span className="topic-actions">
                    <button type="button" className="link" onClick={() => setReplacing(provider)}>
                      Replace
                    </button>
                    <button type="button" className="link danger" onClick={() => setRemoving(provider)}>
                      Remove
                    </button>
                  </span>
                )}
              </div>
              {!in_settings && (!has || replacing === provider) && (
                <KeyForm
                  api={api}
                  provider={provider}
                  onGiven={() => given(provider)}
                  onCancel={has ? () => setReplacing(null) : undefined}
                />
              )}
              {removing === provider && (
                <div className="confirm" role="alertdialog" aria-label={`Remove the ${name} key`}>
                  <p>Remove the {name} key? The app can't use {name} without it.</p>
                  <div className="actions">
                    <button type="button" className="danger" onClick={() => remove(provider)}>
                      Yes, remove it
                    </button>
                    <button type="button" className="link" onClick={() => setRemoving(null)}>
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </li>
          )
        })}
      </ul>
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
