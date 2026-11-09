import type { SpeechModels } from './api'

// the speech model the student chose to read their audio, kept in their browser
const CHOSEN = 'qubit-notes:speech-model'

export function chosenSpeechModel(): string | null {
  try {
    return localStorage.getItem(CHOSEN)
  } catch {
    return null
  }
}

export function chooseSpeechModel(model: string) {
  try {
    localStorage.setItem(CHOSEN, model)
  } catch {
    // the app's own reads it, as it does when none is chosen
  }
}

/** The one chosen, if it is still one of them; else the app's own. */
export function speechModelIn(models: SpeechModels, chosen: string | null): string {
  return chosen && models.models.some((m) => m.id === chosen) ? chosen : models.default
}
