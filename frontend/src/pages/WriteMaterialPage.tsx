import { useEffect, useState, type FormEvent } from 'react'
import type { Course, StudyApi } from '../api'
import { Markdown } from '../components/Markdown'
import { slug } from '../names'
import { href, navigate } from '../router'

type Props = {
  api: StudyApi
  courseId: string
  subject: string
  topic: string
}

// the filename a name is saved under, as the backend makes it: "Shape functions" is "shape-functions.md"
function filenameOf(name: string): string {
  const stem = slug(name.trim().replace(/\.md$/i, ''))
  return stem ? `${stem}.md` : ''
}

/** Writes a Markdown material in a topic: typed or pasted, previewed formatted, then saved and processed. */
export function WriteMaterialPage({ api, courseId, subject, topic }: Props) {
  const [course, setCourse] = useState<Course | null>(null)
  const [name, setName] = useState('')
  const [text, setText] = useState('')
  const [tab, setTab] = useState<'write' | 'preview'>('write')
  const [leaving, setLeaving] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  const back = () => navigate({ page: 'course', courseId })
  const filename = filenameOf(name)

  async function save(event: FormEvent) {
    event.preventDefault()
    if (!course) return
    if (!filename) {
      setError('Give the material a name with at least one letter or digit')
      return
    }
    if (!text.trim()) {
      setError('Write something first')
      return
    }
    setSaving(true)
    setError(null)
    try {
      await api.writeMaterial(course.name, subject, topic, name, text)
      back()
    } catch (e) {
      setError((e as Error).message)
      setSaving(false)
    }
  }

  function cancel() {
    if (text.trim()) setLeaving(true)
    else back()
  }

  return (
    <section className="write-material" aria-labelledby="write-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'course', courseId })}>
          ← Back to the course
        </a>
        <h2 id="write-title">
          Write material in {subject} › {topic}
        </h2>
      </header>

      <form className="editor card" aria-label="Write material" onSubmit={save}>
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Shape functions" required />
        </label>
        {filename && (
          <p className="note" aria-live="polite">
            Saved as <code>{filename}</code>
          </p>
        )}

        <div className="tabs" role="tablist" aria-label="Editor">
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'write'}
            className={tab === 'write' ? 'tab selected' : 'tab'}
            onClick={() => setTab('write')}
          >
            Write
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'preview'}
            className={tab === 'preview' ? 'tab selected' : 'tab'}
            onClick={() => setTab('preview')}
          >
            Preview
          </button>
        </div>

        {tab === 'write' ? (
          <label>
            Text
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={24}
              spellCheck
              autoFocus
              placeholder={'# 1 Introduction\nType or paste Markdown here.'}
            />
          </label>
        ) : (
          <article className="section-text preview" aria-label="Preview">
            {text.trim() ? <Markdown text={text} headingOffset={3} /> : <p className="note">Nothing to preview yet.</p>}
          </article>
        )}

        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}

        {leaving ? (
          <div className="confirm" role="alertdialog" aria-label="Leave without saving">
            <p>Leave without saving? What you wrote will be lost.</p>
            <div className="actions">
              <button type="button" className="danger" onClick={back}>
                Discard
              </button>
              <button type="button" className="link" onClick={() => setLeaving(false)}>
                Keep writing
              </button>
            </div>
          </div>
        ) : (
          <div className="actions">
            <button type="submit" disabled={saving || !course}>
              {saving ? 'Saving…' : 'Save'}
            </button>
            <button type="button" className="link" onClick={cancel} disabled={saving}>
              Cancel
            </button>
          </div>
        )}
      </form>
    </section>
  )
}
