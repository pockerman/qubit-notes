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

// the reviews, and the cards not reviewed, shown of each subject
const HISTORY = 50
// how many are asked for, to have those of each subject
const FETCHED = 5000

const plural = (count: number, one: string) => `${count} ${one}${count === 1 ? '' : 's'}`

// how long until a card was due again; a card forgotten is due again the same day
const dueAgainIn = (days: number) => (days === 0 ? '10 minutes' : plural(days, 'day'))

const inScope = (card: ReviewCard, { courseId, subject, documentId, section }: ReviewScope) =>
  card.course_id === courseId &&
  (!subject || card.subject === subject) &&
  (!documentId || card.source.document_id === documentId) &&
  (!section || card.source.section === section)

/** The cards by what `key` gives each, with their first's order. */
function groups<K>(cards: ReviewCard[], key: (card: ReviewCard) => K): [K, ReviewCard[]][] {
  const grouped = new Map<K, ReviewCard[]>()
  for (const card of cards) grouped.set(key(card), [...(grouped.get(key(card)) ?? []), card])
  return [...grouped]
}

/** The flashcards due for review, a card for each course with how many are due, as in My courses. A course shows its
 * subjects and sections, each with how many; choosing one reviews its cards one at a time: the student turns it over
 * and says how well they remembered it, which decides when it is due again. Below, History: the reviews they have made
 * and the cards they have not reviewed yet (features/ui_reviews.feature). */
export function ReviewsPage({ api, scope }: { api: StudyApi; scope?: ReviewScope }) {
  const [due, setDue] = useState<Due | null>(null)
  const [history, setHistory] = useState<ReviewRecord[] | null>(null)
  const [notReviewed, setNotReviewed] = useState<ReviewCard[]>([])
  // the courses' titles, by id
  const [titles, setTitles] = useState<Record<string, string>>({})
  const [turned, setTurned] = useState(false)
  const [reviewing, setReviewing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.reviews().then(setDue, (e: Error) => setError(e.message))
    api.reviewHistory(FETCHED).then(setHistory, (e: Error) => setError(e.message))
    api.notReviewed(FETCHED).then(setNotReviewed, (e: Error) => setError(e.message))
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
      load()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setReviewing(false)
    }
  }

  const cards = due && scope ? due.cards.filter((c) => inScope(c, scope)) : (due?.cards ?? [])
  // a course is chosen from; a subject or a section of it is reviewed
  const chosen = Boolean(scope?.subject || scope?.section)
  const card = chosen ? cards[0] : undefined

  return (
    <section className="reviews" aria-labelledby="reviews-title">
      <header className="page-header">
        {chosen && scope ? (
          <a className="link" href={href({ page: 'reviews', scope: { courseId: scope.courseId } })}>
            ← Sections
          </a>
        ) : (
          <a className="link" href={href(scope ? { page: 'reviews' } : { page: 'courses' })}>
            {scope ? '← All my courses' : '← My courses'}
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
            : scope
              ? 'Nothing left to review here.'
              : 'Nothing to review now.' +
                (due.next_due_at ? ` The next card is due ${new Date(due.next_due_at).toLocaleString()}.` : '')}
        </p>
      )}
      {scope && <h3>{titles[scope.courseId]}</h3>}
      {!scope && cards.length > 0 && <Courses cards={cards} titles={titles} />}
      {scope && !chosen && cards.length > 0 && <Sections courseId={scope.courseId} cards={cards} />}
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
      {history && <History reviews={history} notReviewed={notReviewed} titles={titles} scope={scope} />}
    </section>
  )
}

/** A card for each course with cards due, and how many. */
function Courses({ cards, titles }: { cards: ReviewCard[]; titles: Record<string, string> }) {
  const courses = groups(cards, (c) => c.course_id)
    .map(([courseId, due]) => ({ courseId, due, title: titles[courseId] ?? due[0].source.filename }))
    .sort((a, b) => a.title.localeCompare(b.title))
  return (
    <nav aria-label="Cards due">
      <ul className="course-cards">
        {courses.map(({ courseId, due, title }) => (
          <li key={courseId}>
            <a className="card course-card" href={href({ page: 'reviews', scope: { courseId } })}>
              <strong>{title}</strong>
              <span className="note">{plural(due.length, 'card')}</span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}

/** A course's subjects, to review all of one, each with a card for each section with cards due. A paper has no
 * subject: its sections are alone. */
function Sections({ courseId, cards }: { courseId: string; cards: ReviewCard[] }) {
  const subjects = groups(cards, (c) => c.subject ?? '').sort(([, a], [, b]) =>
    (a[0].subject_name ?? '').localeCompare(b[0].subject_name ?? ''),
  )
  return (
    <nav aria-label="Cards due">
      {subjects.map(([subject, ofSubject]) => (
        <div key={subject}>
          {subject && (
            <h4>
              <a href={href({ page: 'reviews', scope: { courseId, subject } })}>
                {ofSubject[0].subject_name ?? subject} · {plural(ofSubject.length, 'card')}
              </a>
            </h4>
          )}
          <ul className="course-cards">
            {groups(ofSubject, (c) => `${c.source.document_id}-${c.source.section}`)
              .sort(
                ([, [a]], [, [b]]) =>
                  a.source.filename.localeCompare(b.source.filename) || a.source.section - b.source.section,
              )
              .map(([key, ofSection]) => {
                const { document_id: documentId, section, title, filename } = ofSection[0].source
                return (
                  <li key={key}>
                    <a
                      className="card course-card"
                      href={href({ page: 'reviews', scope: { courseId, documentId, section } })}
                    >
                      <strong>{title}</strong>
                      <span className="note">
                        {plural(ofSection.length, 'card')} · {filename}
                      </span>
                    </a>
                  </li>
                )
              })}
          </ul>
        </div>
      ))}
    </nav>
  )
}

type HistoryProps = {
  reviews: ReviewRecord[]
  notReviewed: ReviewCard[]
  titles: Record<string, string>
  scope?: ReviewScope
}

/** What the student has reviewed, then what they haven't, of each subject on its own: all of them, those of the course
 * they are in, or the one they are reviewing, a section's being its material's subject. */
function History({ reviews, notReviewed, titles, scope }: HistoryProps) {
  const documentOf = (item: ReviewRecord | ReviewCard) =>
    'document_id' in item ? item.document_id : item.source.document_id
  const inSubject =
    scope?.subject ?? [...reviews, ...notReviewed].find((item) => documentOf(item) === scope?.documentId)?.subject
  const shown = (item: ReviewRecord | ReviewCard) =>
    (!scope || item.course_id === scope.courseId) && (!inSubject || item.subject === inSubject)

  const subjects = new Map<string, { title: string; reviews: ReviewRecord[]; cards: ReviewCard[] }>()
  const subjectOf = (item: ReviewRecord | ReviewCard) => {
    const key = `${item.course_id}/${item.subject ?? ''}`
    const found = subjects.get(key) ?? {
      title: [titles[item.course_id], item.subject_name].filter(Boolean).join(' › '),
      reviews: [],
      cards: [],
    }
    subjects.set(key, found)
    return found
  }
  for (const review of reviews.filter(shown)) subjectOf(review).reviews.push(review)
  for (const card of notReviewed.filter(shown)) subjectOf(card).cards.push(card)

  return (
    <section className="card" aria-labelledby="review-history-title">
      <h3 id="review-history-title">History</h3>
      {subjects.size === 0 ? (
        <p className="note">You haven't reviewed any cards yet.</p>
      ) : (
        [...subjects]
          .sort(([, a], [, b]) => a.title.localeCompare(b.title))
          .map(([key, subject]) => (
            <div key={key}>
              <h4>{subject.title}</h4>
              <div className="table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th scope="col">Reviewed</th>
                      <th scope="col">Card</th>
                      <th scope="col">Remembered</th>
                      <th scope="col">Due again in</th>
                    </tr>
                  </thead>
                  <tbody>
                    {subject.reviews.slice(0, HISTORY).map((review) => (
                      <tr key={review.id}>
                        <td>{new Date(review.reviewed_at).toLocaleString()}</td>
                        <td>
                          <Markdown text={review.front} />
                        </td>
                        <td>{REMEMBERED.find(({ answer }) => answer === review.answer)?.label ?? review.answer}</td>
                        <td>{dueAgainIn(review.interval_after)}</td>
                      </tr>
                    ))}
                    {subject.cards.slice(0, HISTORY).map((card) => (
                      <tr key={card.id}>
                        <td>Not reviewed yet</td>
                        <td>
                          <Markdown text={card.front} />
                        </td>
                        <td>—</td>
                        <td>—</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))
      )}
    </section>
  )
}
