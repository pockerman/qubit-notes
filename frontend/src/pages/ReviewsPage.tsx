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

/** The flashcards to review: first the subjects, each a card with how many cards it has, due or not, and nothing else.
 * A subject shows its sections, each with how many, and its History: the reviews made and the cards not reviewed yet.
 * Choosing a section reviews its cards due one at a time: the student turns it over and says how well they remembered it, which
 * decides when it is due again (features/ui_reviews.feature). */
export function ReviewsPage({ api, scope }: { api: StudyApi; scope?: ReviewScope }) {
  const [due, setDue] = useState<Due | null>(null)
  // every card to review, due or not
  const [every, setEvery] = useState<ReviewCard[] | null>(null)
  const [history, setHistory] = useState<ReviewRecord[] | null>(null)
  const [notReviewed, setNotReviewed] = useState<ReviewCard[]>([])
  // the courses' titles, by id
  const [titles, setTitles] = useState<Record<string, string>>({})
  const [turned, setTurned] = useState(false)
  const [reviewing, setReviewing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const [dueNow, cards, reviews, waiting] = await Promise.all([
        api.reviews(),
        api.reviewCards(),
        api.reviewHistory(FETCHED),
        api.notReviewed(FETCHED),
      ])
      setDue(dueNow)
      setEvery(cards)
      setHistory(reviews)
      setNotReviewed(waiting)
    } catch (e) {
      setError((e as Error).message)
    }
  }, [api])

  useEffect(() => {
    void load()
  }, [load])

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
      await load()
      setTurned(false)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setReviewing(false)
    }
  }

  const here = (cards: ReviewCard[]) => (scope ? cards.filter((c) => inScope(c, scope)) : cards)
  const cards = here(due?.cards ?? [])
  const allCards = here(every ?? [])
  const nextDue = allCards.length > 0 ? Math.min(...allCards.map((c) => Date.parse(c.due_at))) : null
  // a section is reviewed; a subject is chosen from
  const chosen = Boolean(scope?.section)
  const card = chosen ? cards[0] : undefined

  const heading = scope && allCards.length > 0 ? allCards[0].subject_name || titles[scope.courseId] : undefined

  return (
    <section className="reviews" aria-labelledby="reviews-title">
      <header className="page-header">
        {scope && (
          <a
            className="link"
            href={href({
              page: 'reviews',
              ...(chosen ? { scope: { courseId: scope.courseId, subject: scope.subject } } : {}),
            })}
          >
            {chosen ? '← Sections' : '← Subjects'}
          </a>
        )}
        <h2 id="reviews-title">Reviews</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {due && every && (scope || allCards.length === 0) && (
        <p role="status" className="note">
          {cards.length > 0
            ? `${plural(cards.length, 'card')} due`
            : scope
              ? 'Nothing left to review here.' +
                (nextDue ? ` The next card is due ${new Date(nextDue).toLocaleString()}.` : '')
              : 'Nothing to review now.'}
        </p>
      )}
      {heading && <h3>{heading}</h3>}
      {!scope && allCards.length > 0 && <Subjects cards={allCards} titles={titles} />}
      {scope && !chosen && allCards.length > 0 && <Sections scope={scope} cards={allCards} />}
      {every && !scope && allCards.length === 0 && (
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
      {scope && history && <History reviews={history} notReviewed={notReviewed} titles={titles} scope={scope} />}
    </section>
  )
}

/** A card for each subject with cards, and how many; a collection of papers has none, so is one itself. */
function Subjects({ cards, titles }: { cards: ReviewCard[]; titles: Record<string, string> }) {
  const subjects = groups(cards, (c) => `${c.course_id}/${c.subject ?? ''}`)
    .map(([key, ofSubject]) => {
      const { course_id: courseId, subject, subject_name: name } = ofSubject[0]
      const course = titles[courseId] ?? ofSubject[0].source.filename
      return { key, ofSubject, course, title: name || course, scope: { courseId, ...(subject ? { subject } : {}) } }
    })
    .sort((a, b) => a.title.localeCompare(b.title) || a.course.localeCompare(b.course))
  // subjects of different courses may be called the same
  const named = (title: string) => subjects.filter((s) => s.title === title).length
  return (
    <nav aria-label="Cards">
      <ul className="course-cards">
        {subjects.map(({ key, ofSubject, course, title, scope }) => (
          <li key={key}>
            <a className="card course-card" href={href({ page: 'reviews', scope })}>
              <strong>{named(title) > 1 ? `${title} (${course})` : title}</strong>
              <span className="note">{plural(ofSubject.length, 'card')}</span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}

/** A card for each section with cards, and how many. */
function Sections({ scope, cards }: { scope: ReviewScope; cards: ReviewCard[] }) {
  return (
    <nav aria-label="Cards">
      <ul className="course-cards">
        {groups(cards, (c) => `${c.source.document_id}-${c.source.section}`)
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
                  href={href({ page: 'reviews', scope: { ...scope, documentId, section } })}
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
    </nav>
  )
}

type HistoryProps = {
  reviews: ReviewRecord[]
  notReviewed: ReviewCard[]
  titles: Record<string, string>
  scope: ReviewScope
}

/** What the student has reviewed of the subject, then what they haven't. */
function History({ reviews, notReviewed, titles, scope }: HistoryProps) {
  const shown = (item: ReviewRecord | ReviewCard) =>
    item.course_id === scope.courseId && (!scope.subject || item.subject === scope.subject)

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
