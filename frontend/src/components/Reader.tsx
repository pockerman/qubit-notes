import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import type { NewNote, Note, OpenedMaterial, SectionText, StudyApi } from '../api'
import { formatMoment } from '../moments'
import { NotesPanel } from './NotesPanel'

type Props = {
  api: StudyApi
  courseId: string
  documentId: string
  onClose: () => void
}

function sectionLabel(title: string, filename: string): string {
  return title || filename
}

// the words selected in one section of the text, to take a note on
type Selection = { section: number; passage: string }

function selectedPassage(): Selection | null {
  const selection = window.getSelection()
  const passage = selection?.toString().trim()
  if (!selection || !passage || selection.rangeCount === 0) return null
  const sectionOf = (node: Node | null) =>
    (node instanceof Element ? node : node?.parentElement)?.closest<HTMLElement>('[data-section]')
  const start = sectionOf(selection.anchorNode)
  // a note is on the words of a single section
  if (!start || start !== sectionOf(selection.focusNode)) return null
  return { section: Number(start.dataset.section), passage }
}

/** The paragraph, with the passages that have notes marked. */
function highlight(paragraph: string, passages: Note[]): ReactNode {
  const marks = passages
    .map((note) => ({ note, at: note.passage ? paragraph.indexOf(note.passage) : -1 }))
    .filter(({ at }) => at >= 0)
    .sort((a, b) => a.at - b.at)
  const parts: ReactNode[] = []
  let cursor = 0
  for (const { note, at } of marks) {
    if (at < cursor) continue
    parts.push(paragraph.slice(cursor, at))
    parts.push(
      <mark key={note.id} title={note.text}>
        {note.passage}
      </mark>,
    )
    cursor = at + (note.passage?.length ?? 0)
  }
  parts.push(paragraph.slice(cursor))
  return parts
}

type NoteFormProps = {
  label: string
  onSave: (text: string) => Promise<void>
  onCancel: () => void
}

function NoteForm({ label, onSave, onCancel }: NoteFormProps) {
  const [text, setText] = useState('')
  return (
    <form
      className="note-form card"
      aria-label="New note"
      onSubmit={async (e) => {
        e.preventDefault()
        await onSave(text)
      }}
    >
      <p className="note">{label}</p>
      <label>
        Note
        <textarea value={text} onChange={(e) => setText(e.target.value)} rows={3} required autoFocus />
      </label>
      <div className="actions">
        <button type="submit">Save note</button>
        <button type="button" className="link" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

export function Reader({ api, courseId, documentId, onClose }: Props) {
  const [material, setMaterial] = useState<OpenedMaterial | null>(null)
  const [position, setPosition] = useState<number | null>(null)
  const [parts, setParts] = useState<SectionText[]>([])
  const [notes, setNotes] = useState<Note[]>([])
  const [selection, setSelection] = useState<Selection | null>(null)
  // a new note on the video, at this moment
  const [moment, setMoment] = useState<number | null>(null)
  // where the video is, for the "Add note at" button
  const [playhead, setPlayhead] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const video = useRef<HTMLVideoElement>(null)

  const loadNotes = useCallback(() => {
    api.notes(courseId, documentId).then(setNotes, (e: Error) => setError(e.message))
  }, [api, courseId, documentId])

  useEffect(() => {
    api.openMaterial(courseId, documentId).then(
      (opened) => {
        setMaterial(opened)
        setPosition(opened.sections[0]?.position ?? null)
        loadNotes()
      },
      (e: Error) => setError(e.message),
    )
  }, [api, courseId, documentId, loadNotes])

  useEffect(() => {
    if (position === null) return
    api.readSection(courseId, documentId, position).then(setParts, (e: Error) => setError(e.message))
  }, [api, courseId, documentId, position])

  async function download() {
    if (!material) return
    try {
      const url = URL.createObjectURL(await api.download(courseId, documentId))
      const link = document.createElement('a')
      link.href = url
      link.download = material.filename
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function addNote(note: NewNote) {
    try {
      await api.addNote(courseId, documentId, note)
      setSelection(null)
      setMoment(null)
      window.getSelection()?.removeAllRanges()
      setError(null)
      loadNotes()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function changeNote(note: Note, text: string) {
    try {
      await api.changeNote(note.id, text)
      loadNotes()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function deleteNote(note: Note) {
    try {
      await api.deleteNote(note.id)
      loadNotes()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  function goTo(note: Note) {
    if (note.at_seconds !== null && video.current) {
      video.current.currentTime = note.at_seconds
      void video.current.play().catch(() => undefined)
    } else if (note.section !== null) {
      // the note may be in a subsection of the section being read
      if (!parts.some((part) => part.section.position === note.section)) setPosition(note.section)
    }
  }

  const panel = <NotesPanel notes={notes} onGoTo={goTo} onChange={changeNote} onDelete={deleteNote} />

  return (
    <section className="reader" aria-labelledby="reader-title">
      <header className="reader-header">
        <button type="button" className="link" onClick={onClose}>
          ← Back
        </button>
        <h2 id="reader-title">{material?.filename ?? 'Opening…'}</h2>
        {material && (
          <>
            <span className="note">
              {material.subject} › {material.topic}
            </span>
            <button type="button" onClick={download}>
              Download
            </button>
          </>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {material?.kind === 'video' && (
        <div className="reader-body video">
          <div>
            <video
              ref={video}
              controls
              preload="metadata"
              src={api.fileUrl(courseId, documentId)}
              aria-label={material.filename}
              onTimeUpdate={(e) => setPlayhead(e.currentTarget.currentTime)}
            />
            {moment === null ? (
              <button type="button" onClick={() => setMoment(playhead)}>
                Add note at {formatMoment(playhead)}
              </button>
            ) : (
              <NoteForm
                label={`At ${formatMoment(moment)}`}
                onSave={(text) => addNote({ text, at_seconds: moment })}
                onCancel={() => setMoment(null)}
              />
            )}
          </div>
          {panel}
        </div>
      )}

      {material?.kind === 'text' && (
        <div className="reader-body">
          <nav aria-label="Sections" className="outline">
            <ol>
              {material.sections.map((section) => (
                <li key={section.position} style={{ paddingLeft: `${(section.level - 1) * 0.9}rem` }}>
                  <button
                    type="button"
                    className={section.position === position ? 'section-link selected' : 'section-link'}
                    aria-current={section.position === position ? 'true' : undefined}
                    onClick={() => setPosition(section.position)}
                  >
                    {sectionLabel(section.title, material.filename)}
                  </button>
                </li>
              ))}
            </ol>
          </nav>

          <div>
            <article
              className="section-text"
              aria-label="Section text"
              onMouseUp={() => setSelection(selectedPassage())}
            >
              {parts.map(({ section, content }, i) => {
                const Heading = i === 0 ? 'h3' : 'h4'
                const passages = notes.filter((note) => note.section === section.position)
                return (
                  <section key={section.position} data-section={section.position}>
                    <Heading>{sectionLabel(section.title, material.filename)}</Heading>
                    {content
                      .split(/\n\s*\n/)
                      .filter((paragraph) => paragraph.trim())
                      .map((paragraph, j) => (
                        <p key={j}>{highlight(paragraph, passages)}</p>
                      ))}
                  </section>
                )
              })}
            </article>
            {selection && (
              <NoteForm
                label={`On “${selection.passage}”`}
                onSave={(text) => addNote({ text, ...selection })}
                onCancel={() => setSelection(null)}
              />
            )}
          </div>

          {panel}
        </div>
      )}
    </section>
  )
}
