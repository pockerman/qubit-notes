import { useState } from 'react'
import type { Attempt, OutOfDate, Quiz, Scope, Source, StudyApi, Summary } from '../api'
import { Markdown } from './Markdown'

type Props = {
  api: StudyApi
  scope: Scope
  // what the scope is, e.g. "2 Shape functions" or "the whole document"
  label: string
}

function Cited({ sources }: { sources: Source[] }) {
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
  ].filter(Boolean)
  return (
    <p role="status" className="warning">
      Out of date: {changes.join('; ')} since it was written.
    </p>
  )
}

function SummaryCard({ api, scope, label }: Props) {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [earlier, setEarlier] = useState<Summary[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function ask(fresh: boolean) {
    setBusy(true)
    setError(null)
    try {
      setSummary(await api.summary(scope, fresh))
      setEarlier((await api.summaries(scope)).slice(1))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card study-card" aria-label="Summary">
      <h4>Summary of {label}</h4>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {summary ? (
        <>
          <Stale outOfDate={summary.out_of_date} />
          <Markdown text={summary.content} />
          <Cited sources={summary.sources} />
          <div className="actions">
            <button type="button" disabled={busy} onClick={() => ask(true)}>
              {busy ? 'Writing…' : 'Write a new summary'}
            </button>
          </div>
          {earlier.length > 0 && (
            <details>
              <summary>Earlier summaries ({earlier.length})</summary>
              {earlier.map((s) => (
                <article key={s.id} className="earlier">
                  <p className="note">{new Date(s.created_at).toLocaleString()}</p>
                  <Markdown text={s.content} />
                </article>
              ))}
            </details>
          )}
        </>
      ) : (
        <button type="button" disabled={busy} onClick={() => ask(false)}>
          {busy ? 'Writing…' : 'Summarise'}
        </button>
      )}
    </section>
  )
}

function QuizCard({ api, scope, label }: Props) {
  const [count, setCount] = useState(5)
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [answers, setAnswers] = useState<(number | null)[]>([])
  const [attempt, setAttempt] = useState<Attempt | null>(null)
  const [scores, setScores] = useState<Attempt[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function ask(fresh: boolean) {
    setBusy(true)
    setError(null)
    try {
      const got = await api.quiz(scope, count, fresh)
      setQuiz(got)
      setAnswers(got.questions.map(() => null))
      setAttempt(null)
      setScores(await api.attempts(got.id))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function submit() {
    if (!quiz) return
    try {
      setAttempt(await api.takeQuiz(quiz.id, answers))
      setScores(await api.attempts(quiz.id))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  function retake() {
    if (!quiz) return
    setAnswers(quiz.questions.map(() => null))
    setAttempt(null)
  }

  return (
    <section className="card study-card" aria-label="Quiz">
      <h4>Quiz on {label}</h4>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <label className="inline">
          Questions
          <input
            type="number"
            min={1}
            max={20}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>
        <button type="button" disabled={busy} onClick={() => ask(false)}>
          {busy ? 'Writing…' : 'Quiz me'}
        </button>
        {quiz && (
          <button type="button" className="link" disabled={busy} onClick={() => ask(true)}>
            New quiz
          </button>
        )}
      </div>

      {quiz && (
        <form
          aria-label="Questions"
          onSubmit={(e) => {
            e.preventDefault()
            void submit()
          }}
        >
          <Stale outOfDate={quiz.out_of_date} />
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
                          name={`question-${i}`}
                          checked={answers[i] === j}
                          onChange={() => setAnswers(answers.map((a, k) => (k === i ? j : a)))}
                        />
                        {choice}
                      </label>
                    ))}
                  </fieldset>
                  {result && !result.correct && (
                    <p className="note">
                      The answer is “{question.choices[result.correct_choice]}”. Study again:{' '}
                      {result.source.filename} › {result.source.title}
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
              <button type="button" className="link" onClick={retake}>
                Take it again
              </button>
            </div>
          ) : (
            <button type="submit">Check my answers</button>
          )}
        </form>
      )}

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

/** Summaries and quizzes of a scope. Give it a key per scope, so another scope starts afresh. */
export function StudyTools({ api, scope, label }: Props) {
  return (
    <div className="study-tools">
      <SummaryCard api={api} scope={scope} label={label} />
      <QuizCard api={api} scope={scope} label={label} />
    </div>
  )
}
