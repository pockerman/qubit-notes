/** The model providers, as students know them. */
export const PROVIDER: Record<string, string> = { anthropic: 'Anthropic', openai: 'OpenAI', voyage: 'Voyage AI' }

// told when an admin gives the app a key, so the platform's status checks it again
export const KEY_GIVEN = 'qubit-notes:key-given'
