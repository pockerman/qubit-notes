import { useState, type FormEvent } from 'react'
import type { Course, StudyApi } from '../api'
import { slug } from '../names'

// a topic in a subject the student names, or in `inSubject` when the course has it already
export function NewTopicForm({
  api,
  course,
  inSubject,
  inSubjectName,
  onCreated,
}: {
  api: StudyApi
  course: Course
  inSubject?: string
  // what `inSubject` is called
  inSubjectName?: string
  onCreated: () => void
}) {
  const [subject, setSubject] = useState(inSubject ?? '')
  const [topic, setTopic] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!slug(subject) || !slug(topic)) {
      setError('Subject and topic each need at least one letter or digit')
      return
    }
    try {
      // known by their ids, and shown by the names typed; a subject the course has keeps its name
      await api.createTopic(course.name, slug(subject), slug(topic), inSubject ? undefined : subject, topic)
      onCreated()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card" aria-label={inSubject ? `New topic in ${inSubjectName}` : 'New topic'} onSubmit={submit}>
      {!inSubject && (
        <label>
          Subject
          <input
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Distributed systems"
            required
          />
        </label>
      )}
      <label>
        Topic
        <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Introduction" required />
      </label>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <button type="submit">Create topic</button>
    </form>
  )
}
