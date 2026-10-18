import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { Attempt, OutOfDate, Quiz, Scope, Source, StudyApi, Turn } from '../api'
import { Markdown } from './Markdown'

type Props = {
  api: StudyApi
  // where the student is: a section of a material, or a topic
  where: Scope
  // what the conversation is on, e.g. the material's filename or the topic
  label: string
  onClose: () => void
}

function Cited({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null
  return (
    <details className="cited">
      <summary>From {sources.length === 1 ? '1 section' : `${sources.length} sections`}</summary>
      <ul>
        {sources.map((source) => (
          <li key={`${source.document_id}-${source.section}`}>
            {source.filename} › {source.title}
          </li>
        ))}
      </ul>
    </details>
  )
}

function Stale({ outOfDate }: { outOfDate: OutOfDate | null }) {
  if (!outOfDate) return null
  const changes = [
    outOfDate.added.length ? `${outOfDate.added.join(', ')} added` : '',
    outOfDate.removed.length ? `${outOfDate.removed.join(', ')} removed` : '',
    outOfDate.edited?.length ? `${outOfDate.edited.join(', ')} edited` : '',
  ].filter(Boolean)
  return (
    <p role="status" className="warning">
      Out of date: {changes.join('; ')} since it was written.
    </p>
  )
}

/** A quiz to take, with the student's scores on it. */
function QuizView({ api, quiz }: { api: StudyApi; quiz: Quiz }) {
  const [answers, setAnswers] = useState<(number | null)[]>(() => quiz.questions.map(() => null))
  const [attempt, setAttempt] = useState<Attempt | null>(null)
  const [scores, setScores] = useState<Attempt[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.attempts(quiz.id).then(setScores, () => undefined)
  }, [api, quiz.id])

  async function submit(event: FormEvent) {
    event.preventDefault()
    try {
      setAttempt(await api.takeQuiz(quiz.id, answers))
      setScores(await api.attempts(quiz.id))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <section className="study-card" aria-label="Quiz">
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <Stale outOfDate={quiz.out_of_date} />
      <form aria-label="Questions" onSubmit={submit}>
        <ol className="questions">
          {quiz.questions.map((question, i) => {
            const result = attempt?.results[i]
            return (
              <li key={i} className={result ? (result.correct ? 'right' : 'wrong') : undefined}>
                <fieldset disabled={Boolean(attempt)}>
                  <legend>{question.question}</legend>
                  {question.choices.map((choice, j) => (
                    <label key={j} className={result && j === result.correct_choice ? 'choice correct' : 'choice'}>
                      <input
                        type="radio"
                        name={`${quiz.id}-question-${i}`}
                        checked={answers[i] === j}
                        onChange={() => setAnswers(answers.map((a, k) => (k === i ? j : a)))}
                      />
                      {choice}
                    </label>
                  ))}
                </fieldset>
                {result && !result.correct && (
                  <p className="note">
                    The answer is “{question.choices[result.correct_choice]}”. Study again: {result.source.filename}{' '}
                    › {result.source.title}
                  </p>
                )}
              </li>
            )
          })}
        </ol>
        {attempt ? (
          <div className="actions">
            <p role="status" className="score">
              You scored {attempt.score} out of {attempt.total}
            </p>
            <button
              type="button"
              className="link"
              onClick={() => {
                setAnswers(quiz.questions.map(() => null))
                setAttempt(null)
              }}
            >
              Take it again
            </button>
          </div>
        ) : (
          <button type="submit">Check my answers</button>
        )}
      </form>
      {scores.length > 0 && (
        <details>
          <summary>My scores ({scores.length})</summary>
          <ul aria-label="My scores">
            {scores.map((s) => (
              <li key={s.id}>
                {s.score} of {s.total} · {new Date(s.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        </details>
      )}
    </section>
  )
}

function Reply({ api, turn }: { api: StudyApi; turn: Turn }) {
  if (turn.kind === 'summary') {
    if (!turn.summary) return <p className="note">This summary was deleted with its material.</p>
    return (
      <section className="study-card" aria-label="Summary">
        <Stale outOfDate={turn.summary.out_of_date} />
        <Markdown text={turn.summary.content} />
        <Cited sources={turn.summary.sources} />
      </section>
    )
  }
  if (turn.kind === 'quiz') {
    if (!turn.quiz) return <p className="note">This quiz was deleted with its material.</p>
    return <QuizView api={api} quiz={turn.quiz} />
  }
  return (
    <section aria-label="Answer" className={turn.covered ? undefined : 'not-covered'}>
      <Markdown text={turn.answer} />
      <Cited sources={turn.sources} />
    </section>
  )
}

/** The assistant: the student asks in their own words, for answers, summaries and quizzes. */
export function Assistant({ api, where, label, onClose }: Props) {
  const [turns, setTurns] = useState<Turn[] | null>(null)
  const [question, setQuestion] = useState('')
  const [asking, setAsking] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const end = useRef<HTMLDivElement>(null)
  // the conversation is on the material or the topic, whichever section is being read
  const about: Scope = where.document_id
    ? { course_id: where.course_id, document_id: where.document_id }
    : { course_id: where.course_id, subject: where.subject, topic: where.topic }
  const aboutKey = JSON.stringify(about)

  useEffect(() => {
    api.conversation(JSON.parse(aboutKey)).then(
      (conversation) => setTurns(conversation.turns),
      (e: Error) => setError(e.message),
    )
  }, [api, aboutKey])

  useEffect(() => {
    end.current?.scrollIntoView?.({ block: 'nearest' })
  }, [turns, asking])

  async function ask(event: FormEvent) {
    event.preventDefault()
    const text = question.trim()
    if (!text) return
    setError(null)
    setAsking(text)
    setQuestion('')
    try {
      const turn = await api.ask(where, text)
      setTurns((earlier) => [...(earlier ?? []), turn])
    } catch (e) {
      setError((e as Error).message)
      setQuestion(text)
    } finally {
      setAsking(null)
    }
  }

  async function startAgain() {
    try {
      await api.startAgain(about)
      setTurns([])
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <aside className="assistant" aria-label="Assistant">
      <header className="assistant-header">
        <h3>Assistant</h3>
        <span className="note">on {label}</span>
        <button type="button" className="link" onClick={startAgain} disabled={!turns?.length || asking !== null}>
          New conversation
        </button>
        <button type="button" className="link" aria-label="Close the assistant" onClick={onClose}>
          ✕
        </button>
      </header>

      <ol className="turns" aria-label="Conversation">
        {turns?.length === 0 && !asking && (
          <li className="note">
            Ask about your material, or ask for a summary or a quiz, e.g. “Summarise this section” or “Quiz me with 5
            questions on the whole document”.
          </li>
        )}
        {turns?.map((turn) => (
          <li key={turn.id} className="turn">
            <p className="asked">{turn.question}</p>
            <Reply api={api} turn={turn} />
          </li>
        ))}
        {asking && (
          <li className="turn">
            <p className="asked">{asking}</p>
            <p role="status" className="note">
              Thinking…
            </p>
          </li>
        )}
      </ol>
      <div ref={end} />

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <form className="ask" aria-label="Ask the assistant" onSubmit={ask}>
        <label>
          Ask the assistant
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                e.currentTarget.form?.requestSubmit()
              }
            }}
            rows={2}
            disabled={asking !== null}
          />
        </label>
        <button type="submit" disabled={asking !== null || !question.trim()}>
          Ask
        </button>
      </form>
    </aside>
  )
}
