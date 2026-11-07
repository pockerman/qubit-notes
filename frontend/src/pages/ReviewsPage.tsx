import { useCallback, useEffect, useState } from 'react'
import type { Due, Remembered, ReviewCard, ReviewRecord, StudyApi } from '../api'
import { Markdown } from '../components/Markdown'
import { href, type ReviewScope } from '../router'

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

const inScope = (card: ReviewCard, { courseId, subject, documentId, section }: ReviewScope) =>
  (!courseId || card.course_id === courseId) &&
  (!subject || card.subject === subject) &&
  (!documentId || card.source.document_id === documentId) &&
  (!section || card.source.section === section)

/** The cards by what `key` gives each, with their first's order. */
function groups<K>(cards: ReviewCard[], key: (card: ReviewCard) => K): [K, ReviewCard[]][] {
  const grouped = new Map<K, ReviewCard[]>()
  for (const card of cards) grouped.set(key(card), [...(grouped.get(key(card)) ?? []), card])
  return [...grouped]
}

/** The flashcards due for review in the student's courses, by course, subject, material and section, to choose what to review;
 * then those, one at a time: the student turns it over and says how well they remembered it, which decides when it is
 * due again. Below, the reviews they have made (features/ui_reviews.feature). */
export function ReviewsPage({ api, scope }: { api: StudyApi; scope?: ReviewScope }) {
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
    // cards of papers are in collections, which aren't among the courses
    Promise.all([api.courses(), api.collections()]).then(
      ([courses, collections]) =>
        setTitles(Object.fromEntries([...courses, ...collections].map((c) => [c.id, c.title]))),
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

  const cards = due && scope ? due.cards.filter((c) => inScope(c, scope)) : (due?.cards ?? [])
  const card = scope ? cards[0] : undefined

  return (
    <section className="reviews" aria-labelledby="reviews-title">
      <header className="page-header">
        {scope ? (
          <a className="link" href={href({ page: 'reviews' })}>
            ← Everything due
          </a>
        ) : (
          <a className="link" href={href({ page: 'courses' })}>
            ← My courses
          </a>
        )}
        <h2 id="reviews-title">Reviews</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {due && (
        <p role="status" className="note">
          {cards.length > 0
            ? `${plural(cards.length, 'card')} due`
            : scope?.courseId
              ? 'Nothing left to review here.'
              : 'Nothing to review now.' +
                (due.next_due_at ? ` The next card is due ${new Date(due.next_due_at).toLocaleString()}.` : '')}
        </p>
      )}
      {!scope && cards.length > 0 && <CardsDue cards={cards} titles={titles} />}
      {due && !scope && cards.length === 0 && !due.next_due_at && (
        <p className="note">Ask the assistant for flashcards, e.g. “Make flashcards of this section”, to review them.</p>
      )}
      {card && (
        <article className="card review-card" aria-label="Card">
          <p className="note">
            {[titles[card.course_id] ?? card.source.filename, card.subject_name, card.source.filename]
              .filter(Boolean)
              .join(' · ')}{' '}
            › {card.source.title}
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

/** What is due, to choose what to review: all of it, or a course, a subject, a material or a section. */
function CardsDue({ cards, titles }: { cards: ReviewCard[]; titles: Record<string, string> }) {
  const courseTitle = (id: string, of: ReviewCard[]) => titles[id] ?? of[0].source.filename
  const courses = groups(cards, (c) => c.course_id).sort(([a, ofA], [b, ofB]) =>
    courseTitle(a, ofA).localeCompare(courseTitle(b, ofB)),
  )
  return (
    <nav className="card review-groups" aria-label="Cards due">
      <Choice scope={{}} label="All my cards" count={cards.length} />
      <ul>
        {courses.map(([courseId, ofCourse]) => (
          <li key={courseId}>
            <Choice scope={{ courseId }} label={courseTitle(courseId, ofCourse)} count={ofCourse.length} />
            <ul>
              {groups(ofCourse, (c) => c.subject ?? '')
                .sort(([, a], [, b]) => (a[0].subject_name ?? '').localeCompare(b[0].subject_name ?? ''))
                .map(([subject, ofSubject]) =>
                  // a paper has no subject: its material is directly under its collection
                  subject ? (
                    <li key={subject}>
                      <Choice
                        scope={{ courseId, subject }}
                        label={ofSubject[0].subject_name ?? subject}
                        count={ofSubject.length}
                      />
                      <ul>
                        <Materials courseId={courseId} cards={ofSubject} />
                      </ul>
                    </li>
                  ) : (
                    <Materials key="" courseId={courseId} cards={ofSubject} />
                  ),
                )}
            </ul>
          </li>
        ))}
      </ul>
    </nav>
  )
}

/** The materials of the cards, each with its sections. */
function Materials({ courseId, cards }: { courseId: string; cards: ReviewCard[] }) {
  return groups(cards, (c) => c.source.document_id)
    .sort(([, a], [, b]) => a[0].source.filename.localeCompare(b[0].source.filename))
    .map(([documentId, ofMaterial]) => (
      <li key={documentId}>
        <Choice scope={{ courseId, documentId }} label={ofMaterial[0].source.filename} count={ofMaterial.length} />
        <ul>
          {groups(ofMaterial, (c) => c.source.section)
            .sort(([a], [b]) => a - b)
            .map(([section, ofSection]) => (
              <li key={section}>
                <Choice
                  scope={{ courseId, documentId, section }}
                  label={ofSection[0].source.title}
                  count={ofSection.length}
                />
              </li>
            ))}
        </ul>
      </li>
    ))
}

function Choice({ scope, label, count }: { scope: ReviewScope; label: string; count: number }) {
  return <a href={href({ page: 'reviews', scope })}>{`${label} · ${plural(count, 'card')}`}</a>
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
