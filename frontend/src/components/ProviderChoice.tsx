import { useEffect, useState } from 'react'
import type { AIModel, StudyApi } from '../api'
import { KEY_GIVEN, PROVIDER, PROVIDER_CHOSEN, chooseProvider, chosenProvider } from '../providers'

/** The providers the app has keys for, to choose which answers: offered only where there are two or more. The
 * choice is the student's, kept in their browser, for all the AI does for them. */
export function ProviderChoice({ api }: { api: StudyApi }) {
  const [inUse, setInUse] = useState<AIModel | null>(null)
  const [chosen, setChosen] = useState(chosenProvider)

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

  if (!inUse || providers.length < 2) return null
  const model = (p: string) => (p === inUse.provider ? inUse.model : inUse.defaults[p])

  return (
    <label className="provider-choice">
      <span aria-hidden="true">AI</span>
      <select aria-label="AI" value={provider} onChange={(e) => chooseProvider(e.target.value)}>
        {providers.map((p) => (
          <option key={p} value={p}>
            {PROVIDER[p] ?? p} · {model(p)}
          </option>
        ))}
      </select>
    </label>
  )
}
