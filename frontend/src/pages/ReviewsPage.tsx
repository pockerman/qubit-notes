import { useCallback, useEffect, useState } from 'react'
import type { Due, Remembered, ReviewRecord, StudyApi } from '../api'
import { Markdown } from '../components/Markdown'
import { href } from '../router'

const REMEMBERED: { answer: Remembered; label: string }[] = [
  { answer: 'again', label: 'Again' },
  { answer: 'hard', label: 'Hard' },
  { answer: 'good', label: 'Good' },
  { answer: 'easy', label: 'Easy' },
]

// the reviews shown
const HISTORY = 50

const plural = (count: number, one: string) => `${count} ${one}${count === 1 ? '' : 's'}`

// how long until a card was due again; a card forgotten is due again the same day
const dueAgainIn = (days: number) => (days === 0 ? '10 minutes' : plural(days, 'day'))

/** The flashcards due for review in all the student's courses, one at a time: the student turns it over and says how
 * well they remembered it, which decides when it is due again; below, the reviews they have made
 * (features/ui_reviews.feature). */
export function ReviewsPage({ api }: { api: StudyApi }) {
  const [due, setDue] = useState<Due | null>(null)
  const [history, setHistory] = useState<ReviewRecord[] | null>(null)
  // the courses' titles, by id
  const [titles, setTitles] = useState<Record<string, string>>({})
  const [turned, setTurned] = useState(false)
  const [reviewing, setReviewing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.reviews().then(setDue, (e: Error) => setError(e.message))
    api.reviewHistory(HISTORY).then(setHistory, (e: Error) => setError(e.message))
  }, [api])

  useEffect(load, [load])

  useEffect(() => {
    api.courses().then(
      (courses) => setTitles(Object.fromEntries(courses.map((c) => [c.id, c.title]))),
      () => undefined,
    )
  }, [api])

  async function review(cardId: string, remembered: Remembered) {
    setReviewing(true)
    setError(null)
    try {
      await api.review(cardId, remembered)
      setTurned(false)
      setDue(await api.reviews())
      setHistory(await api.reviewHistory(HISTORY))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setReviewing(false)
    }
  }

  const card = due?.cards[0]

  return (
    <section className="reviews" aria-labelledby="reviews-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'courses' })}>
          ← My courses
        </a>
        <h2 id="reviews-title">Reviews</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {due && (
        <p role="status" className="note">
          {card
            ? `${plural(due.cards.length, 'card')} due`
            : 'Nothing to review now.' +
              (due.next_due_at ? ` The next card is due ${new Date(due.next_due_at).toLocaleString()}.` : '')}
        </p>
      )}
      {due && !card && !due.next_due_at && (
        <p className="note">Ask the assistant for flashcards, e.g. “Make flashcards of this section”, to review them.</p>
      )}
      {card && (
        <article className="card review-card" aria-label="Card">
          <p className="note">
            {titles[card.course_id] ?? card.source.filename} · {card.source.filename} › {card.source.title}
          </p>
          <Markdown text={card.front} />
          {turned ? (
            <>
              <div className="back" aria-label="Its answer">
                <Markdown text={card.back} />
              </div>
              <div className="actions" role="group" aria-label="How well did you remember it?">
                {REMEMBERED.map(({ answer, label }) => (
                  <button key={answer} type="button" disabled={reviewing} onClick={() => review(card.id, answer)}>
                    {label}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <form
              onSubmit={(event) => {
                event.preventDefault()
                setTurned(true)
              }}
            >
              <button type="submit">Show the answer</button>
            </form>
          )}
        </article>
      )}
      {history && <History reviews={history} titles={titles} />}
    </section>
  )
}

function History({ reviews, titles }: { reviews: ReviewRecord[]; titles: Record<string, string> }) {
  return (
    <section className="card" aria-labelledby="review-history-title">
      <h3 id="review-history-title">History</h3>
      {reviews.length === 0 ? (
        <p className="note">You haven't reviewed any cards yet.</p>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">Reviewed</th>
                <th scope="col">Card</th>
                <th scope="col">Course</th>
                <th scope="col">Remembered</th>
                <th scope="col">Due again in</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id}>
                  <td>{new Date(review.reviewed_at).toLocaleString()}</td>
                  <td>
                    <Markdown text={review.front} />
                  </td>
                  <td>{titles[review.course_id] ?? ''}</td>
                  <td>{REMEMBERED.find(({ answer }) => answer === review.answer)?.label ?? review.answer}</td>
                  <td>{dueAgainIn(review.interval_after)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
