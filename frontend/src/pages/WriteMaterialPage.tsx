import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import type { Course, StudyApi, Topic } from '../api'
import { AddImage } from '../components/AddImage'
import { AddReference } from '../components/AddReference'
import { Markdown, type ImageRenderer } from '../components/Markdown'
import { useImageDrafts } from '../imageDrafts'
import { slug } from '../names'
import { brokenReferences, leaveNotice } from '../notices'
import { insertAtCursor, referenceLinks, useReferencesIn } from '../referenceLinks'
import { href, navigate } from '../router'

type Props = {
  api: StudyApi
  courseId: string
  subject: string
  topic: string
  // what to start from, e.g. material the AI wrote; empty if not given
  initial?: { name: string; text: string }
  // whether the student chooses the topic to save it in; else it's saved in `subject` › `topic`
  chooseTopic?: boolean
}

// the filename a name is saved under, as the backend makes it: "Shape functions" is "shape-functions.md"
function filenameOf(name: string): string {
  const stem = slug(name.trim().replace(/\.md$/i, ''))
  return stem ? `${stem}.md` : ''
}

/** Writes a Markdown material in a topic: typed or pasted, previewed formatted, then saved and processed. */
export function WriteMaterialPage({ api, courseId, subject, topic, initial, chooseTopic = false }: Props) {
  const [course, setCourse] = useState<Course | null>(null)
  const [name, setName] = useState(initial?.name ?? '')
  const [text, setText] = useState(initial?.text ?? '')
  // the topics it can be saved in, and the one chosen, as "subject/topic"
  const [topics, setTopics] = useState<Topic[]>([])
  const [savingIn, setSavingIn] = useState(`${subject}/${topic}`)
  const [tab, setTab] = useState<'write' | 'preview'>('write')
  const [leaving, setLeaving] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const textarea = useRef<HTMLTextAreaElement>(null)
  const images = useImageDrafts({ text, setText, textarea, setError })
  const references = useReferencesIn(api, courseId, text, tab === 'preview')

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  useEffect(() => {
    if (!chooseTopic || !course) return
    api.topics(course.name).then(setTopics, (e: Error) => setError(e.message))
  }, [api, course, chooseTopic])

  const back = () => navigate({ page: 'topic', courseId, subject, topic })
  const filename = filenameOf(name)

  const preview: ImageRenderer = useMemo(
    () => (src, alt, key) => {
      const added = images.drafts.get(src)
      if (added || /^https:/i.test(src)) {
        return <img key={key} className="material-image" src={added?.url ?? src} alt={alt} referrerPolicy="no-referrer" />
      }
      return (
        <span key={key} className="image-missing" role="group" aria-label={`Missing image ${src}`}>
          Missing image: <code>{src}</code>
        </span>
      )
    },
    [images.drafts],
  )

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
      const [inSubject, inTopic] = savingIn.split('/')
      const upload = await api.writeMaterial(course.name, inSubject, inTopic, name, text)
      const failed = await images.keepWith(api, upload.course_id, upload.document_id, text)
      if (failed.length) {
        setError(`${filename} was saved, but not all its images: ${failed.join('; ')}`)
        setSaving(false)
        return
      }
      const broken = brokenReferences(filename, upload.broken_references)
      if (broken) leaveNotice(broken)
      navigate({ page: 'topic', courseId, subject: inSubject, topic: inTopic })
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
        <a className="link" href={href({ page: 'topic', courseId, subject, topic })}>
          ← Back to the topic
        </a>
        <h2 id="write-title">
          {initial ? 'Material the AI wrote' : 'Write material'} in {subject} › {topic}
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
        {chooseTopic && (
          <label>
            Save in
            <select value={savingIn} onChange={(e) => setSavingIn(e.target.value)}>
              {topics.length === 0 && (
                <option value={`${subject}/${topic}`}>
                  {subject} › {topic}
                </option>
              )}
              {topics.map((t) => (
                <option key={`${t.subject}/${t.topic}`} value={`${t.subject}/${t.topic}`}>
                  {t.subject} › {t.topic}
                </option>
              ))}
            </select>
          </label>
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
              ref={textarea}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onPaste={(e) => images.pasteOrDrop(e.clipboardData?.files, e)}
              onDrop={(e) => images.pasteOrDrop(e.dataTransfer?.files, e)}
              rows={24}
              spellCheck
              autoFocus
              placeholder={'# 1 Introduction\nType or paste Markdown here.'}
            />
          </label>
        ) : (
          <article className="section-text preview" aria-label="Preview">
            {text.trim() ? (
              <Markdown
                text={text}
                headingOffset={3}
                image={preview}
                reference={referenceLinks(courseId, references)}
              />
            ) : (
              <p className="note">Nothing to preview yet.</p>
            )}
          </article>
        )}

        {tab === 'write' && <AddImage onInsert={images.insert} />}
        {tab === 'write' && (
          <AddReference
            api={api}
            courseId={courseId}
            onInsert={(reference) => insertAtCursor(text, setText, textarea, reference)}
          />
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
