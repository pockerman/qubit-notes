import { useState, type FormEvent } from 'react'
import { waitForUpload, type StudyApi } from '../api'

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

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) return
    const form = event.currentTarget
    const target = course ?? courseName.trim()
    setBusy(true)
    setMessage({ text: `Uploading ${file.name}…` })
    try {
      const upload = await api.upload(`${target}/${subject.trim()}/${topic.trim()}`, file)
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
          <input value={courseName} onChange={(e) => setCourseName(e.target.value)} placeholder="aeronautics" required />
        </label>
      )}
      <label>
        Subject
        <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="numerical-methods" required />
      </label>
      <label>
        Topic
        <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="finite-elements" required />
      </label>
      <label>
        File
        <input
          type="file"
          accept=".txt,.md,.pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          required
        />
      </label>
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
