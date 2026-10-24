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
  // called once the upload is accepted, with where it went; it's processed after
  onUploaded: (upload: Upload, where: { subject: string; topic: string; filename: string }) => void
  // called once a topic is created without a file, with its ids
  onTopicCreated?: (where: { subject: string; topic: string }) => void
  // what the topic given is called, e.g. "Numerical methods › Finite elements": it is uploaded there, not asked
  topicName?: string
}

export function UploadForm({
  api,
  course,
  subject: initialSubject = '',
  topic: initialTopic = '',
  onUploaded,
  onTopicCreated,
  topicName,
}: Props) {
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
  // what the button does: a file is uploaded to its topic; without one, the topic, or only the subject, is created
  const action = file || topicName ? 'Upload' : topic.trim() ? 'Create topic' : 'Create subject'

  // a subject, or a topic, without material
  async function create() {
    setBusy(true)
    try {
      if (!topic.trim()) {
        const created = await api.createSubject(course, subject.trim())
        // the subject stays filled in, for a topic to be added to it
        setMessage({ text: `Created the subject ${created.name}. Fill in a topic to add one to it.` })
      } else {
        await api.createTopic(course, names[0], names[1], subject.trim(), topic.trim())
        onTopicCreated?.({ subject: names[0], topic: names[1] })
      }
    } catch (e) {
      setMessage({ text: (e as Error).message, error: true })
    }
    setBusy(false)
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!names[0]) {
      setMessage({ text: 'The subject needs at least one letter or digit', error: true })
      return
    }
    if (topic.trim() && !names[1]) {
      setMessage({ text: 'The topic needs at least one letter or digit', error: true })
      return
    }
    if (!file) return create()
    if (!names[1]) {
      setMessage({ text: 'Fill in the topic the file goes in', error: true })
      return
    }
    setBusy(true)
    setMessage({ text: `Uploading ${file.name}…` })
    try {
      const upload = await api.upload(`${course}/${names.join('/')}`, file)
      if (subject !== initialSubject || topic !== initialTopic) {
        // a topic the student named, which the upload made: shown by the names typed, unless it had names already
        await api.createTopic(course, names[0], names[1], subject.trim(), topic.trim())
      }
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
      onUploaded(upload, { subject: names[0], topic: names[1], filename: file.name })
    } catch (e) {
      setMessage({ text: (e as Error).message, error: true })
      setBusy(false)
    }
  }

  return (
    <form className="upload" onSubmit={submit} aria-label={`Upload to ${course}`}>
      {topicName ? (
        <p className="note">To {topicName}</p>
      ) : (
        <>
          <label>
            Subject
            <input
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Numerical methods"
              required
            />
          </label>
          <label>
            Topic
            <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Finite elements" />
          </label>
        </>
      )}
      <label>
        File
        <input
          type="file"
          accept=".txt,.md,.pdf,.epub,.mp4,.webm"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          // only to add to a topic given; otherwise the subject or topic can be created without one
          required={Boolean(topicName)}
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
        {action}
      </button>
      {message && (
        <p role={message.error ? 'alert' : 'status'} className={message.error ? 'error' : 'note'}>
          {message.text}
        </p>
      )}
    </form>
  )
}
