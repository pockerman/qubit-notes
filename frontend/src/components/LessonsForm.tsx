import { useState, type FormEvent } from 'react'
import { waitForLessons, type Course, type StudyApi } from '../api'

/** Makes the subject's lessons from a PDF, an EPUB or a Markdown file: a topic of each of its headings at its top
 * level, with the text up to the next as its material (features/ui_lessons.feature). */
export function LessonsForm({
  api,
  course,
  subject,
  subjectName,
  onMade,
}: {
  api: StudyApi
  course: Course
  subject: string
  subjectName: string
  // called with how many lessons were made
  onMade: (count: number) => void
}) {
  const [file, setFile] = useState<File | null>(null)
  const [making, setMaking] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!file) return
    setError(null)
    setMaking(file.name)
    try {
      const started = await api.makeLessons(course.name, subject, file)
      const made = await waitForLessons(api, started.id)
      if (made.status === 'failed') setError(made.error ?? `The lessons could not be made from ${file.name}`)
      else onMade(made.topics.length)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setMaking(null)
    }
  }

  return (
    <form className="card" aria-label={`Make lessons in ${subjectName}`} onSubmit={submit}>
      <p className="note">
        Each heading of the document becomes a topic, with its text up to the next heading. A book is divided into its
        chapters.
      </p>
      <label>
        PDF, EPUB or Markdown file
        <input
          type="file"
          accept=".pdf,.epub,.md"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          disabled={making !== null}
        />
      </label>
      {making && (
        <p role="status" className="note">
          Making lessons from {making}…
        </p>
      )}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <button type="submit" disabled={!file || making !== null}>
          Make lessons
        </button>
      </div>
    </form>
  )
}
