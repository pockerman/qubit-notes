/** The model providers, as students know them. */
export const PROVIDER: Record<string, string> = { anthropic: 'Anthropic', openai: 'OpenAI', voyage: 'Voyage AI' }

// told when an admin gives the app a key, or removes one, so the platform's status and the choice of provider check
// again
export const KEY_GIVEN = 'qubit-notes:key-given'

// the provider the student chose to answer them, kept in their browser, and told when they choose another
const CHOSEN = 'qubit-notes:ai-provider'
export const PROVIDER_CHOSEN = 'qubit-notes:provider-chosen'

export function chosenProvider(): string | null {
  try {
    return localStorage.getItem(CHOSEN)
  } catch {
    return null
  }
}

export function chooseProvider(provider: string) {
  try {
    localStorage.setItem(CHOSEN, provider)
  } catch {
    // the app's own provider answers, as it does when none is chosen
  }
  window.dispatchEvent(new Event(PROVIDER_CHOSEN))
}

/** The header that asks the app to answer with the provider chosen, if one is; the app's answers otherwise, as it
 * does where it hasn't the provider's key. */
export function providerHeader(): Record<string, string> {
  const provider = chosenProvider()
  return provider ? { 'X-AI-Provider': provider } : {}
}
