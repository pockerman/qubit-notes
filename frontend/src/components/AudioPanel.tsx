import { useEffect, useState, type FormEvent } from 'react'
import type { MaterialAudio, SpeechModels, StudyApi } from '../api'
import { chosenSpeechModel, speechModelIn } from '../speechModels'
import { SpeechModelChoice } from './SpeechModelChoice'

type Props = {
  api: StudyApi
  courseId: string
  documentId: string
  // what the audio is of, e.g. the material's filename
  label: string
  onClose: () => void
}

// how often a student's audio is asked after while it is made
const POLL_MS = 2000

/** The student's audio of a material, beside its text: made with instructions, played, improved and deleted. */
export function AudioPanel({ api, courseId, documentId, label, onClose }: Props) {
  // undefined until it is known whether there is any
  const [audio, setAudio] = useState<MaterialAudio | null | undefined>(undefined)
  const [file, setFile] = useState<{ url: string; filename: string } | null>(null)
  const [instructions, setInstructions] = useState('')
  const [suggestions, setSuggestions] = useState('')
  const [improving, setImproving] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [models, setModels] = useState<SpeechModels | null>(null)
  const [chosen, setChosen] = useState(chosenSpeechModel)
  const model = models ? speechModelIn(models, chosen) : null
  const nameOf = (id: string) => models?.models.find((m) => m.id === id)?.name ?? id

  useEffect(() => {
    api.audio(courseId, documentId).then(setAudio, (e: Error) => setError(e.message))
  }, [api, courseId, documentId])

  useEffect(() => {
    api.speechModels().then(setModels, () => setModels(null))
  }, [api])

  // while it is made, it is asked after until it is ready or has failed
  const generating = audio?.status === 'generating'
  useEffect(() => {
    if (!generating) return
    const timer = setInterval(() => {
      api.audio(courseId, documentId).then(setAudio, (e: Error) => setError(e.message))
    }, POLL_MS)
    return () => clearInterval(timer)
  }, [api, courseId, documentId, generating])

  // once ready, its MP3, to play and download; a new one each time it is made again
  const ready = audio?.status === 'ready' ? audio.updated_at : null
  useEffect(() => {
    if (!ready) return
    let url: string | null = null
    let gone = false
    api.audioFile(courseId, documentId).then(
      (downloaded) => {
        if (gone) return
        url = URL.createObjectURL(downloaded.blob)
        setFile({ url, filename: downloaded.filename ?? 'audio.mp3' })
      },
      (e: Error) => setError(e.message),
    )
    return () => {
      gone = true
      if (url) URL.revokeObjectURL(url)
      setFile(null)
    }
  }, [api, courseId, documentId, ready])

  async function run(action: () => Promise<MaterialAudio | null>) {
    setBusy(true)
    setError(null)
    try {
      setAudio(await action())
      return true
    } catch (e) {
      setError((e as Error).message)
      return false
    } finally {
      setBusy(false)
    }
  }

  async function make(event: FormEvent) {
    event.preventDefault()
    await run(() => api.makeAudio(courseId, documentId, instructions, model))
  }

  async function improve(event: FormEvent) {
    event.preventDefault()
    if (await run(() => api.improveAudio(courseId, documentId, suggestions, model))) {
      setImproving(false)
      setSuggestions('')
    }
  }

  async function remove() {
    await run(async () => {
      await api.deleteAudio(courseId, documentId)
      return null
    })
  }

  return (
    <aside className="audio-panel assistant" aria-label="Audio">
      <header className="assistant-header">
        <h3>Audio</h3>
        <span className="note">of {label}</span>
        <button type="button" className="icon" aria-label="Close the audio" onClick={onClose}>
          ✕
        </button>
        {models && model && <SpeechModelChoice models={models} chosen={model} onChoose={setChosen} />}
      </header>

      {audio === null && (
        <form className="audio-form" aria-label="Make the audio" onSubmit={make}>
          <p className="note">
            The AI writes a narration of this material to listen to, formulas said in words, and reads it aloud. Say how
            you'd like it, if you like.
          </p>
          <label>
            Instructions
            <textarea
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows={3}
              maxLength={2000}
              placeholder="e.g. explain it like a lecture, slowly, with an example for each idea"
            />
          </label>
          <button type="submit" disabled={busy}>
            Make audio
          </button>
        </form>
      )}

      {generating && (
        <p role="status" className="note">
          Making the audio… The AI is writing a narration and reading it aloud; this can take a few minutes.
        </p>
      )}

      {audio?.status === 'failed' && (
        <p role="alert" className="error">
          The audio couldn't be made: {audio.error}
        </p>
      )}

      {audio?.status === 'ready' && (
        <>
          {file ? (
            <audio className="audio-player" controls src={file.url} aria-label="Audio player" preload="metadata" />
          ) : (
            <p className="note">Loading the audio…</p>
          )}
          <dl className="made-with" aria-label="Made with">
            <dt>Read by</dt>
            <dd>{nameOf(audio.model)}</dd>
            <dt>Instructions</dt>
            <dd>{audio.instructions || 'none'}</dd>
            {audio.suggestions && (
              <>
                <dt>Suggestions</dt>
                <dd>{audio.suggestions}</dd>
              </>
            )}
          </dl>
          <details className="narration">
            <summary>Narration</summary>
            <div role="group" aria-label="Narration">
              {audio.narration.split(/\n\s*\n/).map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          </details>
        </>
      )}

      {improving && audio?.status === 'ready' && (
        <form className="audio-form" aria-label="Improve the audio" onSubmit={improve}>
          <label>
            Suggestions
            <textarea
              value={suggestions}
              onChange={(e) => setSuggestions(e.target.value)}
              rows={3}
              maxLength={2000}
              required
              autoFocus
              placeholder="e.g. too fast; skip the history; give an example of each shape function"
            />
          </label>
          <div className="actions">
            <button type="submit" disabled={busy || !suggestions.trim()}>
              Make it again
            </button>
            <button type="button" className="secondary" onClick={() => setImproving(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {audio && audio.status !== 'generating' && !improving && (
        <div className="actions">
          {audio.status === 'ready' && file && (
            <a className="button secondary" href={file.url} download={file.filename}>
              Download MP3
            </a>
          )}
          {audio.status === 'ready' && (
            <button type="button" className="secondary" onClick={() => setImproving(true)} disabled={busy}>
              Improve
            </button>
          )}
          <button type="button" className="secondary danger" onClick={remove} disabled={busy}>
            Delete audio
          </button>
        </div>
      )}

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
    </aside>
  )
}
