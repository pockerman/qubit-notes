import type { TranscriptionModels } from './api'

// the transcription model the student chose to hear what they say, kept in their browser
const CHOSEN = 'qubit-notes:transcription-model'

export function chosenTranscriptionModel(): string | null {
  try {
    return localStorage.getItem(CHOSEN)
  } catch {
    return null
  }
}

export function chooseTranscriptionModel(model: string) {
  try {
    localStorage.setItem(CHOSEN, model)
  } catch {
    // the app's own hears it, as it does when none is chosen
  }
}

/** The one chosen, if it is still one of them; else the app's own. */
export function transcriptionModelIn(models: TranscriptionModels, chosen: string | null): string {
  return chosen && models.models.some((m) => m.id === chosen) ? chosen : models.default
}
