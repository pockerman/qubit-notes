import { useEffect, useMemo, useRef, useState, type ClipboardEvent, type DragEvent, type FormEvent } from 'react'
import type { Course, StudyApi } from '../api'
import { Markdown, type ImageRenderer } from '../components/Markdown'
import { IMAGE_ACCEPT } from '../images'
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

const IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']

// where an image is kept with the material: images/<its name>, made unique among those already added
function imagePath(file: File, taken: Set<string>): string {
  const dot = file.name.lastIndexOf('.')
  const extension = dot > 0 ? file.name.slice(dot + 1).toLowerCase() : file.type.replace('image/', '')
  const stem = slug(dot > 0 ? file.name.slice(0, dot) : file.name) || 'image'
  let path = `images/${stem}.${extension}`
  for (let n = 2; taken.has(path); n++) path = `images/${stem}-${n}.${extension}`
  return path
}

function captionOf(file: File): string {
  return file.name.replace(/\.[^.]+$/, '').replace(/[-_]+/g, ' ')
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
  // images added while writing, by their path in the text; they're kept with the material once it's saved
  const [images, setImages] = useState<Map<string, { file: File; url: string }>>(new Map())
  const [addingImage, setAddingImage] = useState(false)
  const [caption, setCaption] = useState('')
  const [picked, setPicked] = useState<File | null>(null)
  const textarea = useRef<HTMLTextAreaElement>(null)

  // the local copies of the images are let go when the page is
  const urls = useRef<string[]>([])
  useEffect(() => () => urls.current.forEach(URL.revokeObjectURL), [])

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  const back = () => navigate({ page: 'course', courseId })
  const filename = filenameOf(name)

  /** keeps the image and puts a reference to it where the cursor is */
  function insertImage(file: File, alt: string) {
    if (!IMAGE_TYPES.includes(file.type)) {
      setError(`${file.name} is not a PNG, JPEG, GIF or WebP image`)
      return
    }
    const path = imagePath(file, new Set(images.keys()))
    const url = URL.createObjectURL(file)
    urls.current.push(url)
    setImages(new Map(images).set(path, { file, url }))
    const reference = `![${alt.replace(/[[\]]/g, '')}](${path})`
    const at = textarea.current?.selectionStart ?? text.length
    const before = text.slice(0, at)
    const after = text.slice(textarea.current?.selectionEnd ?? at)
    // on a line of its own
    const lead = before && !before.endsWith('\n') ? '\n' : ''
    setText(`${before}${lead}${reference}\n${after}`)
    setError(null)
  }

  function pasteOrDrop(files: FileList | undefined, event: ClipboardEvent | DragEvent) {
    const found = [...(files ?? [])].filter((file) => file.type.startsWith('image/'))
    if (!found.length) return
    event.preventDefault()
    found.forEach((file) => insertImage(file, captionOf(file)))
  }

  const preview: ImageRenderer = useMemo(
    () => (src, alt, key) => {
      const added = images.get(src)
      if (added || /^https:/i.test(src)) {
        return <img key={key} className="material-image" src={added?.url ?? src} alt={alt} referrerPolicy="no-referrer" />
      }
      return (
        <span key={key} className="image-missing" role="group" aria-label={`Missing image ${src}`}>
          Missing image: <code>{src}</code>
        </span>
      )
    },
    [images],
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
      const upload = await api.writeMaterial(course.name, subject, topic, name, text)
      const failed: string[] = []
      for (const [path, { file }] of images) {
        // an image whose reference was deleted from the text isn't kept
        if (!text.includes(`](${path})`)) continue
        try {
          await api.addImage(upload.course_id, upload.document_id, file, path)
        } catch (e) {
          failed.push(`${file.name}: ${(e as Error).message}`)
        }
      }
      if (failed.length) {
        setError(`${filename} was saved, but not all its images: ${failed.join('; ')}`)
        setSaving(false)
        return
      }
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
              ref={textarea}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onPaste={(e) => pasteOrDrop(e.clipboardData?.files, e)}
              onDrop={(e) => pasteOrDrop(e.dataTransfer?.files, e)}
              rows={24}
              spellCheck
              autoFocus
              placeholder={'# 1 Introduction\nType or paste Markdown here.'}
            />
          </label>
        ) : (
          <article className="section-text preview" aria-label="Preview">
            {text.trim() ? (
              <Markdown text={text} headingOffset={3} image={preview} />
            ) : (
              <p className="note">Nothing to preview yet.</p>
            )}
          </article>
        )}

        {tab === 'write' &&
          (addingImage ? (
            <div className="add-image" role="group" aria-label="Add an image">
              <label>
                Image
                <input type="file" accept={IMAGE_ACCEPT} onChange={(e) => setPicked(e.target.files?.[0] ?? null)} />
              </label>
              <label>
                Caption
                <input value={caption} onChange={(e) => setCaption(e.target.value)} placeholder="A mesh of triangles" />
              </label>
              <div className="actions">
                <button
                  type="button"
                  disabled={!picked}
                  onClick={() => {
                    if (!picked) return
                    insertImage(picked, caption.trim() || captionOf(picked))
                    setAddingImage(false)
                    setPicked(null)
                    setCaption('')
                  }}
                >
                  Insert
                </button>
                <button type="button" className="link" onClick={() => setAddingImage(false)}>
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p className="note">
              <button type="button" className="link" onClick={() => setAddingImage(true)}>
                Add image
              </button>{' '}
              or paste or drop one into the text. PNG, JPEG, GIF or WebP, up to 10 MB.
            </p>
          ))}

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
