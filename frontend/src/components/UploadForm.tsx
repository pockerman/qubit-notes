import { useState, type FormEvent } from 'react'
import { waitForUpload, type StudyApi } from '../api'
import { slug } from '../names'

type Props = {
  api: StudyApi
  // uploads to this course when set; otherwise the student names the course
  course?: string
  // called with the id of the course uploaded to, once the upload is accepted and again once it is processed
  onUploaded: (courseId: string) => void
}

export function UploadForm({ api, course, onUploaded }: Props) {
  const [courseName, setCourseName] = useState('')
  const [subject, setSubject] = useState('')
  const [topic, setTopic] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null)
  const [busy, setBusy] = useState(false)

  // the location as it's stored, e.g. "computer-science/distributed-systems-design/introduction"
  const names = [course ?? slug(courseName), slug(subject), slug(topic)]
  const location = names.join('/')
  const typed = [course ?? courseName.trim(), subject.trim(), topic.trim()].join('/')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) return
    if (names.some((name) => !name)) {
      setMessage({ text: 'Course, subject and topic each need at least one letter or digit', error: true })
      return
    }
    const form = event.currentTarget
    setBusy(true)
    setMessage({ text: `Uploading ${file.name}…` })
    try {
      const upload = await api.upload(location, file)
      setMessage({ text: `Processing ${file.name}…` })
      onUploaded(upload.course_id)
      const job = await waitForUpload(api, upload.job_id)
      setMessage(
        job.status === 'completed'
          ? { text: `${file.name} is ready` }
          : { text: `${file.name} failed: ${job.error}`, error: true },
      )
      onUploaded(upload.course_id)
      setFile(null)
      setSubject('')
      setTopic('')
      if (course === undefined) setCourseName('')
      form.reset()
    } catch (e) {
      setMessage({ text: (e as Error).message, error: true })
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="upload" onSubmit={submit} aria-label={course ? `Upload to ${course}` : 'Add material'}>
      {course === undefined && (
        <label>
          Course
          <input value={courseName} onChange={(e) => setCourseName(e.target.value)} placeholder="Aeronautics" required />
        </label>
      )}
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
      {names.every(Boolean) && location !== typed && (
        <p className="note" aria-live="polite">
          Saved as <code>{location}</code>
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
