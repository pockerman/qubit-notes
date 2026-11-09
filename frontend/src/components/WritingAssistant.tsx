import { useEffect, useRef, useState, type FormEvent, type RefObject } from 'react'
import type { StudyApi, WritingReply } from '../api'
import { insertAtCursor } from '../referenceLinks'
import { addAtEnd, replaceSection, sectionsOf, withReferences } from '../writing'
import { Markdown } from './Markdown'
import { ProviderChoice } from './ProviderChoice'

type Props = {
  api: StudyApi
  courseId: string
  // the topic the material is written in
  subject: string
  topic: string
  // the material's text, as it is being written, and where its cursor is
  text: string
  setText: (text: string) => void
  textarea: RefObject<HTMLTextAreaElement | null>
  onClose: () => void
}

type Exchange = { request: string; reply: WritingReply }

// the whole material, rather than one of its sections
const WHOLE = ''

/** The writing assistant (features/ui_writing_assistant.feature): it writes material the student asks for, or helps
 * with a section of theirs, from the web, citing it, and its replies go into the material. The conversation lasts
 * while the page is open. */
export function WritingAssistant({ api, courseId, subject, topic, text, setText, textarea, onClose }: Props) {
  const [exchanges, setExchanges] = useState<Exchange[]>([])
  const [request, setRequest] = useState('')
  const [section, setSection] = useState(WHOLE)
  const [searchWeb, setSearchWeb] = useState(true)
  const [asking, setAsking] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const end = useRef<HTMLDivElement>(null)

  const titles = sectionsOf(text).map((s) => s.title)
  // a section chosen that is no longer in the text is no longer chosen
  const chosen = titles.includes(section) ? section : WHOLE

  useEffect(() => {
    end.current?.scrollIntoView?.({ block: 'nearest' })
  }, [exchanges, asking])

  async function ask(event: FormEvent) {
    event.preventDefault()
    const asked = request.trim()
    if (!asked) return
    setError(null)
    setAsking(asked)
    setRequest('')
    try {
      const reply = await api.writingAssistant(courseId, subject, topic, {
        request: asked,
        draft: text,
        section: chosen || null,
        history: exchanges.map((e) => ({ request: e.request, reply: e.reply.reply })),
        search_web: searchWeb,
      })
      setExchanges((earlier) => [...earlier, { request: asked, reply }])
    } catch (e) {
      setError((e as Error).message)
      setRequest(asked)
    } finally {
      setAsking(null)
    }
  }

  return (
    <aside className="assistant writing-assistant" aria-label="Writing assistant">
      <header className="assistant-header">
        <h3>Writing assistant</h3>
        <button
          type="button"
          className="secondary"
          onClick={() => setExchanges([])}
          disabled={exchanges.length === 0 || asking !== null}
        >
          New conversation
        </button>
        <button type="button" className="icon" aria-label="Close the writing assistant" onClick={onClose}>
          ✕
        </button>
        <ProviderChoice api={api} />
      </header>

      <ol className="turns" aria-label="Conversation">
        {exchanges.length === 0 && !asking && (
          <li className="note">
            Ask for material on a subject, e.g. “Write an introduction to the finite element method”, or choose a
            section of yours below and ask for help with it, e.g. “Add a worked example”. It searches the web and cites
            what it draws on.
          </li>
        )}
        {exchanges.map(({ request: asked, reply }, i) => {
          const inserted = withReferences(reply)
          return (
            <li key={i} className="turn">
              <p className="asked">
                {asked}
                {reply.section && <span className="note"> · on {reply.section}</span>}
              </p>
              <article aria-label={`Reply ${i + 1}`} className="writing-reply">
                <Markdown text={reply.reply} headingOffset={3} />
                {reply.sources.length > 0 ? (
                  <ol className="references" aria-label="References">
                    {reply.sources.map((source) => (
                      <li key={source.url}>
                        <a href={source.url} target="_blank" rel="noreferrer">
                          {source.title}
                        </a>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="note">{reply.searched ? 'It cites nothing.' : 'It searched nothing on the web.'}</p>
                )}
                <div className="reply-actions" role="group" aria-label="Put it in the material">
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => insertAtCursor(text, setText, textarea, inserted)}
                  >
                    Insert
                  </button>
                  <button type="button" className="secondary" onClick={() => setText(addAtEnd(text, inserted))}>
                    Add at the end
                  </button>
                  {reply.section && titles.includes(reply.section) && (
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => setText(replaceSection(text, reply.section!, inserted))}
                    >
                      Replace the section
                    </button>
                  )}
                </div>
              </article>
            </li>
          )
        })}
        {asking && (
          <li className="turn">
            <p className="asked">{asking}</p>
            <p role="status" className="note">
              {searchWeb ? 'Searching the web and writing…' : 'Writing…'}
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
      <form className="ask" aria-label="Ask the writing assistant" onSubmit={ask}>
        <label>
          Help with
          <select value={chosen} onChange={(e) => setSection(e.target.value)}>
            <option value={WHOLE}>The whole material</option>
            {titles.map((title, i) => (
              <option key={`${title}-${i}`} value={title}>
                {title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Ask the writing assistant
          <textarea
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                e.currentTarget.form?.requestSubmit()
              }
            }}
            rows={3}
            disabled={asking !== null}
          />
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={searchWeb} onChange={(e) => setSearchWeb(e.target.checked)} />
          Search the web
        </label>
        <button type="submit" disabled={asking !== null || !request.trim()}>
          Ask
        </button>
      </form>
    </aside>
  )
}
