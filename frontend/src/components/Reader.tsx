import { useCallback, useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react'
import {
  waitForUpload,
  type Material,
  type MaterialImages,
  type Neighbours,
  type NewNote,
  type Note,
  type OpenedMaterial,
  type Reference,
  type SectionText,
  type StudyApi,
} from '../api'
import { useImageDrafts } from '../imageDrafts'
import { formatMoment } from '../moments'
import { brokenReferences } from '../notices'
import { insertAtCursor, referenceLinks } from '../referenceLinks'
import { href } from '../router'
import { AddImage } from './AddImage'
import { AddReference } from './AddReference'
import { Assistant } from './Assistant'
import { Markdown, type ImageRenderer } from './Markdown'
import { MaterialImage } from './MaterialImage'
import { NotesPanel } from './NotesPanel'

type Props = {
  api: StudyApi
  courseId: string
  documentId: string
  // the position of the section to open it at; its first if not given
  section?: number
  // whether the student may edit the material: they own the course
  canEdit: boolean
  // back to the material's topic, once it's known which
  onClose: (material: OpenedMaterial | null) => void
}

// the material whose text can be edited
const EDITABLE = ['text/plain', 'text/markdown']

/** Shows a material's images where its Markdown refers to them; images on the web as they are. */
function materialImages(
  api: StudyApi,
  courseId: string,
  documentId: string,
  images: MaterialImages | null,
  onAdd?: (images: MaterialImages) => void,
): ImageRenderer {
  return (src, alt, key) =>
    /^https:/i.test(src) ? (
      <img key={key} className="material-image" src={src} alt={alt} loading="lazy" referrerPolicy="no-referrer" />
    ) : images === null ? (
      <span key={key} className="note">
        Loading image…
      </span>
    ) : (
      <MaterialImage
        key={`${key}:${src}`}
        api={api}
        courseId={courseId}
        documentId={documentId}
        path={src}
        alt={alt}
        missing={!images.images.includes(src)}
        onAdd={onAdd}
      />
    )
}

type EditorProps = {
  api: StudyApi
  courseId: string
  documentId: string
  // Markdown material can have images added as it's edited
  markdown: boolean
  // told of the references of the saved text that are broken, as written
  onSaved: (brokenReferences: string[]) => void
  onCancel: () => void
}

/** Edits the text of a Markdown or text material; once saved, it's processed again. */
function Editor({ api, courseId, documentId, markdown, onSaved, onCancel }: EditorProps) {
  const [text, setText] = useState<string | null>(null)
  const [saving, setSaving] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const textarea = useRef<HTMLTextAreaElement>(null)
  const images = useImageDrafts({ text: text ?? '', setText, textarea, setError })

  useEffect(() => {
    api.materialText(courseId, documentId).then(setText, (e: Error) => setError(e.message))
  }, [api, courseId, documentId])

  async function save(event: FormEvent) {
    event.preventDefault()
    if (text === null) return
    setError(null)
    try {
      setSaving('Saving…')
      const upload = await api.editMaterial(courseId, documentId, text)
      setSaving('Processing your changes…')
      const job = await waitForUpload(api, upload.job_id)
      if (job.status === 'failed') throw new Error(`Processing failed: ${job.error}`)
      const failed = await images.keepWith(api, upload.course_id, upload.document_id, text)
      if (failed.length) throw new Error(`Your changes were saved, but not all the images: ${failed.join('; ')}`)
      onSaved(upload.broken_references)
    } catch (e) {
      setError((e as Error).message)
      setSaving(null)
    }
  }

  return (
    <form className="editor" aria-label="Edit material" onSubmit={save}>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {text === null ? (
        <p className="note">Opening…</p>
      ) : (
        <label>
          Text
          <textarea
            ref={textarea}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onPaste={markdown ? (e) => images.pasteOrDrop(e.clipboardData?.files, e) : undefined}
            onDrop={markdown ? (e) => images.pasteOrDrop(e.dataTransfer?.files, e) : undefined}
            rows={24}
            spellCheck
          />
        </label>
      )}
      {markdown && text !== null && <AddImage onInsert={images.insert} />}
      {markdown && text !== null && (
        <AddReference
          api={api}
          courseId={courseId}
          onInsert={(reference) => insertAtCursor(text, setText, textarea, reference)}
        />
      )}
      <div className="actions">
        <button type="submit" disabled={text === null || saving !== null}>
          Save
        </button>
        <button type="button" className="link" onClick={onCancel} disabled={saving !== null}>
          Cancel
        </button>
        {saving && (
          <span role="status" className="note">
            {saving}
          </span>
        )}
      </div>
    </form>
  )
}

/** a material before or after the one being read, with its topic when it's in another */
function neighbourLabel(neighbour: Material, topic: string): string {
  return neighbour.topic === topic ? neighbour.filename : `${neighbour.filename}, in ${neighbour.topic}`
}

function sectionLabel(title: string, filename: string): string {
  return title || filename
}

// the words selected in one section of the text, to take a note on, and how far down the reader they are
type Selection = { section: number; passage: string; top: number }

function selectedPassage(body: HTMLElement | null): Selection | null {
  const selection = window.getSelection()
  const passage = selection?.toString().trim()
  if (!selection || !passage || selection.rangeCount === 0) return null
  const sectionOf = (node: Node | null) =>
    (node instanceof Element ? node : node?.parentElement)?.closest<HTMLElement>('[data-section]')
  const start = sectionOf(selection.anchorNode)
  // a note is on the words of a single section
  if (!start || start !== sectionOf(selection.focusNode)) return null
  const top = selection.getRangeAt(0).getBoundingClientRect().top - (body?.getBoundingClientRect().top ?? 0)
  return { section: Number(start.dataset.section), passage, top: Math.max(0, top) }
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
  // how far down the reader to open it, beside the passage, to the left of the text
  top?: number
}

function NoteForm({ label, onSave, onCancel, top }: NoteFormProps) {
  const [text, setText] = useState('')
  return (
    <form
      className={top === undefined ? 'note-form card' : 'note-form card beside'}
      style={top === undefined ? undefined : { top }}
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

export function Reader({ api, courseId, documentId, section, canEdit, onClose }: Props) {
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
  const [editing, setEditing] = useState(false)
  // the assistant takes the place of the notes beside the text while it's open
  const [assistant, setAssistant] = useState(false)
  // bumped when the material was edited, so it's opened again
  const [version, setVersion] = useState(0)
  // the images a Markdown material refers to, which it has or is missing
  const [images, setImages] = useState<MaterialImages | null>(null)
  // the references a Markdown material makes to the rest of its course, and what each refers to
  const [references, setReferences] = useState<Reference[] | null>(null)
  // that the text just saved has broken references
  const [saved, setSaved] = useState<string | null>(null)
  // the materials before and after this one, to read on
  const [neighbours, setNeighbours] = useState<Neighbours | null>(null)
  const video = useRef<HTMLVideoElement>(null)
  const body = useRef<HTMLDivElement>(null)

  const loadNotes = useCallback(() => {
    api.notes(courseId, documentId).then(setNotes, (e: Error) => setError(e.message))
  }, [api, courseId, documentId])

  useEffect(() => {
    api.openMaterial(courseId, documentId).then(
      (opened) => {
        setMaterial(opened)
        const at = opened.sections.find((s) => s.position === section) ?? opened.sections[0]
        setPosition(at?.position ?? null)
        loadNotes()
      },
      (e: Error) => setError(e.message),
    )
  }, [api, courseId, documentId, section, loadNotes, version])

  useEffect(() => {
    if (material?.content_type !== 'text/markdown') return
    api.images(courseId, documentId).then(setImages, (e: Error) => setError(e.message))
    api.references(courseId, documentId).then(setReferences, (e: Error) => setError(e.message))
  }, [api, courseId, documentId, material, version])

  useEffect(() => {
    api.neighbours(courseId, documentId).then(setNeighbours, () => setNeighbours(null))
  }, [api, courseId, documentId])

  useEffect(() => {
    if (position === null) return
    api.readSection(courseId, documentId, position).then(setParts, (e: Error) => setError(e.message))
  }, [api, courseId, documentId, position, version])

  // the uploaded file, or a converted material as it is now
  async function download(asItIsNow = false) {
    if (!material) return
    try {
      const file = asItIsNow ? api.export(courseId, documentId) : api.download(courseId, documentId)
      const url = URL.createObjectURL(await file)
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

  const beside = assistant ? (
    <Assistant
      key={documentId}
      api={api}
      where={{ course_id: courseId, document_id: documentId, section: material?.kind === 'text' ? position : null }}
      label={material?.filename ?? ''}
      onClose={() => setAssistant(false)}
    />
  ) : (
    <NotesPanel notes={notes} onGoTo={goTo} onChange={changeNote} onDelete={deleteNote} />
  )
  const markdown = material?.content_type === 'text/markdown'

  return (
    <section className="reader" aria-labelledby="reader-title">
      <header className="reader-header">
        <button type="button" className="link" onClick={() => onClose(material)}>
          ← Back
        </button>
        <h2 id="reader-title">{material?.filename ?? 'Opening…'}</h2>
        {material && (
          <>
            <span className="note">
              {material.subject} › {material.topic}
            </span>
            <div role="group" aria-label="Material actions" className="reader-actions">
              {canEdit && EDITABLE.includes(material.content_type) && !editing && (
                <button
                  type="button"
                  onClick={() => {
                    setSaved(null)
                    setEditing(true)
                  }}
                >
                  Edit
                </button>
              )}
              {material.converted_from ? (
                <>
                  <button type="button" onClick={() => download()}>
                    Download original
                  </button>
                  <button type="button" onClick={() => download(true)}>
                    Download as {material.converted_from.toUpperCase()}
                  </button>
                </>
              ) : (
                <button type="button" onClick={() => download()}>
                  Download
                </button>
              )}
              <button type="button" aria-pressed={assistant} onClick={() => setAssistant(!assistant)}>
                AI
              </button>
            </div>
          </>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {material && neighbours && (neighbours.previous || neighbours.next) && (
        <nav className="reading-order" aria-label="Reading order">
          {neighbours.previous && (
            <a
              className="previous"
              href={href({ page: 'material', courseId, documentId: neighbours.previous.document_id })}
            >
              ← Previous: {neighbourLabel(neighbours.previous, material.topic)}
            </a>
          )}
          {neighbours.next && (
            <a className="next" href={href({ page: 'material', courseId, documentId: neighbours.next.document_id })}>
              Next: {neighbourLabel(neighbours.next, material.topic)} →
            </a>
          )}
        </nav>
      )}

      {saved && !editing && (
        <p role="status" className="warning">
          {saved}
        </p>
      )}

      {editing && (
        <Editor
          api={api}
          courseId={courseId}
          documentId={documentId}
          markdown={material?.content_type === 'text/markdown'}
          onCancel={() => setEditing(false)}
          onSaved={(broken) => {
            setSaved(brokenReferences(material?.filename ?? 'The material', broken))
            setEditing(false)
            setVersion((v) => v + 1)
          }}
        />
      )}

      {!editing && material?.kind === 'video' && (
        <div className={assistant ? 'reader-body video with-assistant' : 'reader-body video'}>
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
          {beside}
        </div>
      )}

      {!editing && material?.kind === 'text' && (
        <div ref={body} className={assistant ? 'reader-body with-assistant' : 'reader-body'}>
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

          <article
            className="section-text"
            aria-label="Section text"
            onMouseUp={() => setSelection(selectedPassage(body.current))}
          >
            {parts.map(({ section, content }, i) => {
              const Heading = i === 0 ? 'h3' : 'h4'
              const passages = notes.filter((note) => note.section === section.position)
              return (
                <section key={section.position} data-section={section.position}>
                  <Heading>{sectionLabel(section.title, material.filename)}</Heading>
                  {markdown ? (
                    <Markdown
                      text={content}
                      headingOffset={3}
                      mark={(text) => highlight(text, passages)}
                      image={materialImages(api, courseId, documentId, images, canEdit ? setImages : undefined)}
                      reference={referenceLinks(courseId, references)}
                    />
                  ) : (
                    content
                      .split(/\n\s*\n/)
                      .filter((paragraph) => paragraph.trim())
                      .map((paragraph, j) => <p key={j}>{highlight(paragraph, passages)}</p>)
                  )}
                </section>
              )
            })}
          </article>

          {beside}

          {selection && (
            <NoteForm
              label={`On “${selection.passage}”`}
              top={selection.top}
              onSave={(text) => addNote({ text, section: selection.section, passage: selection.passage })}
              onCancel={() => setSelection(null)}
            />
          )}
        </div>
      )}
    </section>
  )
}
