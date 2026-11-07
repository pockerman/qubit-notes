import { useEffect, useId, useState } from 'react'
import type { AIModel, StudyApi } from '../api'
import { KEY_GIVEN, PROVIDER, PROVIDER_CHOSEN, chooseProvider, chosenProvider } from '../providers'

/** The providers that can answer, each with its model; one the app has no key for is shown, but can't be chosen, and
 * says why (features/ui_study.feature). The choice is the student's, kept in their browser, for all the AI does for
 * them. */
export function ProviderChoice({ api }: { api: StudyApi }) {
  const [inUse, setInUse] = useState<AIModel | null>(null)
  const [chosen, setChosen] = useState(chosenProvider)
  const name = useId()

  useEffect(() => {
    const load = () => api.aiModel().then(setInUse, () => setInUse(null))
    load()
    const reload = () => setChosen(chosenProvider())
    window.addEventListener(KEY_GIVEN, load)
    window.addEventListener(PROVIDER_CHOSEN, reload)
    return () => {
      window.removeEventListener(KEY_GIVEN, load)
      window.removeEventListener(PROVIDER_CHOSEN, reload)
    }
  }, [api])

  const providers = inUse ? Object.keys(inUse.defaults).filter((p) => inUse.keys[p]) : []
  // the one chosen, if the app has its key; else the app's own, if it has its key; else the first it has
  const provider =
    chosen && providers.includes(chosen)
      ? chosen
      : inUse && providers.includes(inUse.provider)
        ? inUse.provider
        : providers[0]
  // what is shown is what answers
  useEffect(() => {
    if (provider && inUse && provider !== inUse.provider && provider !== chosen) chooseProvider(provider)
  }, [provider, inUse, chosen])

  if (!inUse) return null
  const model = (p: string) => (p === inUse.provider ? inUse.model : inUse.defaults[p])

  return (
    <div className="provider-choice" role="radiogroup" aria-label="AI">
      <span aria-hidden="true">AI</span>
      {Object.keys(inUse.defaults).map((p) => {
        const available = inUse.keys[p]
        const why = `${name}-${p}-why`
        return (
          <span key={p} className={available ? 'provider-option' : 'provider-option unavailable'}>
            <label>
              {/* not disabled, or it could neither be pointed at nor reached to say why */}
              <input
                type="radio"
                name={name}
                checked={p === provider}
                aria-disabled={!available}
                aria-describedby={available ? undefined : why}
                onChange={() => available && chooseProvider(p)}
              />
              {PROVIDER[p] ?? p} · {model(p)}
            </label>
            {!available && (
              <span id={why} role="tooltip" className="provider-tooltip">
                Not available: the API key is missing
              </span>
            )}
          </span>
        )
      })}
    </div>
  )
}
