import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { ComprehensionCheck, Exchange, Scope, Source, StudyApi, TranscriptionModels, Understood } from '../api'
import { chooseTranscriptionModel, chosenTranscriptionModel, transcriptionModelIn } from '../transcriptionModels'
import { Markdown } from './Markdown'
import { ProviderChoice } from './ProviderChoice'

/** What can be checked from where the student is, e.g. "this section" or "the whole material". */
export type Checkable = { label: string; scope: Scope }

type Props = {
  api: StudyApi
  // the first is checked unless the student chooses another
  of: Checkable[]
  // what it is on, e.g. the material's filename or the subject
  label: string
  onClose: () => void
}

const UNDERSTOOD: Record<Understood, string> = { yes: 'Understood', partly: 'Partly understood', no: 'Not understood' }

function from(source: Source): string {
  return `${source.filename} › ${source.title}`
}

function waiting(check: ComprehensionCheck): Exchange | null {
  const last = check.exchanges[check.exchanges.length - 1]
  return last && last.answer === null ? last : null
}

/** Records what the student says with their microphone, until stopped. */
function useRecorder(onRecorded: (recording: Blob) => void) {
  const recorder = useRef<MediaRecorder | null>(null)
  const [recording, setRecording] = useState(false)
  const supported = typeof window !== 'undefined' && 'MediaRecorder' in window && !!navigator.mediaDevices

  useEffect(
    () => () => {
      // stop the microphone if the panel closes while it records
      recorder.current?.stream.getTracks().forEach((track) => track.stop())
    },
    [],
  )

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const started = new MediaRecorder(stream)
    const chunks: Blob[] = []
    started.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data)
    }
    started.onstop = () => {
      stream.getTracks().forEach((track) => track.stop())
      setRecording(false)
      onRecorded(new Blob(chunks, { type: started.mimeType || 'audio/webm' }))
    }
    recorder.current = started
    started.start()
    setRecording(true)
  }

  function stop() {
    recorder.current?.stop()
    recorder.current = null
  }

  return { supported, recording, start, stop }
}

function ExchangeView({ exchange }: { exchange: Exchange }) {
  return (
    <li className="exchange">
      <div className="question">
        <Markdown text={exchange.question} />
      </div>
      <span className="from note">from {from(exchange.source)}</span>
      {exchange.answer !== null && (
        <>
          <p className="answer">{exchange.answer}</p>
          {exchange.spoken && <span className="note">said</span>}
          <div className={`assessment understood-${exchange.understood}`}>
            <strong>{exchange.understood ? UNDERSTOOD[exchange.understood] : ''}</strong>
            {exchange.feedback && <Markdown text={exchange.feedback} />}
            {exchange.cited.length > 0 && <span className="note">As {exchange.cited.map(from).join('; ')} says</span>}
          </div>
        </>
      )}
    </li>
  )
}

function VerdictView({ check }: { check: ComprehensionCheck }) {
  const verdict = check.verdict
  if (!verdict) return null
  const answered = check.exchanges.filter((e) => e.answer !== null)
  const understood = answered.filter((e) => e.understood === 'yes').length
  return (
    <section className="verdict study-card" aria-label="Verdict">
      <h4>
        Verdict: {understood} of {answered.length} understood
      </h4>
      <Markdown text={verdict.summary} />
      {verdict.understood.length > 0 && (
        <>
          <h5>What you understood</h5>
          <ul aria-label="What you understood">
            {verdict.understood.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </>
      )}
      {verdict.to_study.length > 0 && (
        <>
          <h5>To study again</h5>
          <ul aria-label="To study again">
            {verdict.to_study.map((source) => (
              <li key={`${source.document_id}-${source.section}`}>{from(source)}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}

/** The comprehension assistant: it questions the student on what they read or study, assesses their answers, typed
 * or said, and gives its verdict (features/ui_comprehension.feature). */
export function ComprehensionPanel({ api, of, label, onClose }: Props) {
  const [chosen, setChosen] = useState(0)
  const scope = of[chosen]?.scope ?? of[0].scope
  const scopeKey = JSON.stringify(scope)
  const [earlier, setEarlier] = useState<ComprehensionCheck[] | null>(null)
  const [check, setCheck] = useState<ComprehensionCheck | null>(null)
  const [answer, setAnswer] = useState('')
  // whether any of the answer was said rather than typed
  const [spoken, setSpoken] = useState(false)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [models, setModels] = useState<TranscriptionModels | null>(null)
  const [model, setModel] = useState<string | null>(null)
  const end = useRef<HTMLDivElement>(null)
  const recorder = useRecorder(hear)

  useEffect(() => {
    setEarlier(null)
    api.checks(JSON.parse(scopeKey) as Scope).then(setEarlier, (e: Error) => setError(e.message))
  }, [api, scopeKey, check?.id])

  useEffect(() => {
    api.transcriptionModels().then(
      (found) => {
        setModels(found)
        setModel(transcriptionModelIn(found, chosenTranscriptionModel()))
      },
      () => undefined,
    )
  }, [api])

  useEffect(() => {
    end.current?.scrollIntoView?.({ block: 'nearest' })
  }, [check, busy])

  async function run(what: string, action: () => Promise<void>) {
    setError(null)
    setBusy(what)
    try {
      await action()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(null)
    }
  }

  function start() {
    void run('Thinking of a question…', async () => {
      setCheck(await api.startCheck(scope))
      setAnswer('')
      setSpoken(false)
    })
  }

  function takeUp(checkId: string) {
    void run('Opening…', async () => setCheck(await api.check(checkId)))
  }

  function remove(checkId: string) {
    void run('Deleting…', async () => {
      await api.deleteCheck(checkId)
      setEarlier((all) => all?.filter((c) => c.id !== checkId) ?? null)
    })
  }

  function send(event: FormEvent) {
    event.preventDefault()
    if (!check || !answer.trim()) return
    void run('Assessing your answer…', async () => {
      setCheck(await api.answerCheck(check.id, answer, spoken))
      setAnswer('')
      setSpoken(false)
    })
  }

  function endCheck() {
    if (!check) return
    void run('Writing the verdict…', async () => setCheck(await api.endCheck(check.id)))
  }

  function hear(recording: Blob) {
    void run('Hearing what you said…', async () => {
      const heard = await api.transcribe(recording, model)
      if (!heard.text) return
      setAnswer((typed) => (typed.trim() ? `${typed.trimEnd()} ${heard.text}` : heard.text))
      setSpoken(true)
    })
  }

  async function record() {
    setError(null)
    try {
      await recorder.start()
    } catch (e) {
      setError(`The microphone can't be used: ${(e as Error).message}`)
    }
  }

  const question = check && !check.ended_at ? waiting(check) : null
  const answered = check?.exchanges.filter((e) => e.answer !== null).length ?? 0
  const canHear = models?.available ?? false

  return (
    <aside className="assistant comprehension" aria-label="Comprehension check">
      <header className="assistant-header">
        <h3>Check understanding</h3>
        <span className="note">on {label}</span>
        <button type="button" className="icon" aria-label="Close the comprehension check" onClick={onClose}>
          ✕
        </button>
        <ProviderChoice api={api} />
      </header>

      {!check && (
        <div className="check-start">
          {of.length > 1 && (
            <label>
              Check
              <select value={chosen} onChange={(e) => setChosen(Number(e.target.value))} disabled={busy !== null}>
                {of.map((checkable, i) => (
                  <option key={checkable.label} value={i}>
                    {checkable.label}
                  </option>
                ))}
              </select>
            </label>
          )}
          <p className="note">
            The assistant asks you a question at a time on {of.length > 1 ? 'it' : of[0].label}, tells you how well you
            understood it, and when you end the check, what to study again. Answer in your own words, typed or said.
          </p>
          <button type="button" onClick={start} disabled={busy !== null}>
            Start a check
          </button>
          {earlier && earlier.length > 0 && (
            <>
              <h4>Earlier checks</h4>
              <ul className="earlier-checks" aria-label="Earlier checks">
                {earlier.map((c) => {
                  const done = c.exchanges.filter((e) => e.answer !== null)
                  const understood = done.filter((e) => e.understood === 'yes').length
                  return (
                    <li key={c.id}>
                      <span>
                        {new Date(c.created_at).toLocaleString()} ·{' '}
                        {c.ended_at
                          ? `ended, ${understood} of ${done.length} understood`
                          : `${done.length} answered, not ended`}
                      </span>
                      <button type="button" className="secondary" onClick={() => takeUp(c.id)} disabled={busy !== null}>
                        {c.ended_at ? 'See the verdict' : 'Take up'}
                      </button>
                      <button
                        type="button"
                        className="secondary danger"
                        aria-label={`Delete the check of ${new Date(c.created_at).toLocaleString()}`}
                        onClick={() => remove(c.id)}
                        disabled={busy !== null}
                      >
                        Delete
                      </button>
                    </li>
                  )
                })}
              </ul>
            </>
          )}
        </div>
      )}

      {check && (
        <>
          <div className="check-actions">
            <button type="button" className="secondary" onClick={() => setCheck(null)} disabled={busy !== null}>
              ← All checks
            </button>
            {!check.ended_at && (
              <button type="button" onClick={endCheck} disabled={busy !== null || answered === 0}>
                End the check
              </button>
            )}
          </div>
          {check.out_of_date && (
            <p role="status" className="warning">
              The material changed since this check began.
            </p>
          )}
          <ol className="turns exchanges" aria-label="Questions and answers">
            {check.exchanges.map((exchange, i) => (
              <ExchangeView key={i} exchange={exchange} />
            ))}
          </ol>
          <VerdictView check={check} />
          {!check.ended_at && !question && (
            <p className="note">That was the last question: end the check for its verdict.</p>
          )}
        </>
      )}
      <div ref={end} />

      {busy && (
        <p role="status" className="note">
          {busy}
        </p>
      )}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {question && (
        <form className="ask" aria-label="Answer the question" onSubmit={send}>
          <label>
            Your answer
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  e.currentTarget.form?.requestSubmit()
                }
              }}
              rows={4}
              disabled={busy !== null || recorder.recording}
            />
          </label>
          <div className="answer-actions">
            {recorder.supported &&
              (recorder.recording ? (
                <button type="button" className="recording" onClick={recorder.stop}>
                  Stop
                </button>
              ) : (
                <button
                  type="button"
                  className="secondary"
                  onClick={record}
                  disabled={busy !== null || !canHear}
                  title={canHear ? 'Say your answer' : "Not available: the app's OpenAI API key is missing"}
                >
                  Record
                </button>
              ))}
            {models && (
              <label className="note">
                Heard by
                <select
                  value={model ?? models.default}
                  disabled={!canHear || recorder.recording}
                  onChange={(e) => {
                    chooseTranscriptionModel(e.target.value)
                    setModel(e.target.value)
                  }}
                >
                  {models.models.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <button type="submit" disabled={busy !== null || recorder.recording || !answer.trim()}>
              Send
            </button>
          </div>
        </form>
      )}
    </aside>
  )
}
