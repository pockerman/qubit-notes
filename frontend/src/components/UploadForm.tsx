import { useState, type FormEvent } from 'react'
import type { StudyApi, Upload } from '../api'
import { slug } from '../names'
import { IMAGE_ACCEPT } from '../images'

type Props = {
  api: StudyApi
  // the name of the course uploaded to
  course: string
  // the topic to upload to, which the student can change
  subject?: string
  topic?: string
  // called once the upload is accepted; it's processed after
  onUploaded: (upload: Upload) => void
}

export function UploadForm({ api, course, subject: initialSubject = '', topic: initialTopic = '', onUploaded }: Props) {
  const [subject, setSubject] = useState(initialSubject)
  const [topic, setTopic] = useState(initialTopic)
  const [file, setFile] = useState<File | null>(null)
  // a Markdown file's images, matched to what it refers to by their file names
  const [images, setImages] = useState<File[]>([])
  const markdown = file?.name.toLowerCase().endsWith('.md') ?? false
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null)
  const [busy, setBusy] = useState(false)

  // the topic as it's stored, e.g. "distributed-systems/introduction"
  const names = [slug(subject), slug(topic)]
  const typed = `${subject.trim()}/${topic.trim()}`

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) return
    if (names.some((name) => !name)) {
      setMessage({ text: 'Subject and topic each need at least one letter or digit', error: true })
      return
    }
    setBusy(true)
    setMessage({ text: `Uploading ${file.name}…` })
    try {
      const upload = await api.upload(`${course}/${names.join('/')}`, file)
      const failed: string[] = []
      for (const image of markdown ? images : []) {
        setMessage({ text: `Adding ${image.name}…` })
        try {
          await api.addImage(upload.course_id, upload.document_id, image)
        } catch (e) {
          failed.push(`${image.name}: ${(e as Error).message}`)
        }
      }
      if (failed.length) {
        // the material is uploaded; the images that weren't added can be added from the reader
        setMessage({ text: `${file.name} was uploaded, but not all its images: ${failed.join('; ')}`, error: true })
        setBusy(false)
        return
      }
      onUploaded(upload)
    } catch (e) {
      setMessage({ text: (e as Error).message, error: true })
      setBusy(false)
    }
  }

  return (
    <form className="upload" onSubmit={submit} aria-label={`Upload to ${course}`}>
      <label>
        Subject
        <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Numerical methods" required />
      </label>
      <label>
        Topic
        <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Finite elements" required />
      </label>
      <label>
        File
        <input
          type="file"
          accept=".txt,.md,.pdf,.mp4,.webm"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          required
        />
      </label>
      {markdown && (
        <label>
          Images
          <input
            type="file"
            accept={IMAGE_ACCEPT}
            multiple
            onChange={(e) => setImages([...(e.target.files ?? [])])}
          />
          <span className="note">The images the Markdown refers to, e.g. mesh.png for ![…](figures/mesh.png)</span>
        </label>
      )}
      {names.every(Boolean) && names.join('/') !== typed && (
        <p className="note" aria-live="polite">
          Saved as <code>{`${course}/${names.join('/')}`}</code>
        </p>
      )}
      <button type="submit" disabled={busy}>
        Upload
      </button>
      {message && (
        <p role={message.error ? 'alert' : 'status'} className={message.error ? 'error' : 'note'}>
          {message.text}
        </p>
      )}
    </form>
  )
}
