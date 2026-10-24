import { useEffect, useState } from 'react'
import type { Course, StudyApi, Topic } from '../api'
import { UploadForm } from '../components/UploadForm'
import { namesOf } from '../names'
import { brokenReferences, leaveNotice } from '../notices'
import { href, navigate } from '../router'

type Props = {
  api: StudyApi
  courseId: string
  // the topic to add to, if the student came from one
  subject: string
  topic: string
}

export function AddMaterialPage({ api, courseId, subject, topic }: Props) {
  const [course, setCourse] = useState<Course | null>(null)
  // the course's topics, for what the topic given is called
  const [topics, setTopics] = useState<Topic[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  useEffect(() => {
    if (!course) return
    api.topics(course.name).then(setTopics, () => setTopics([]))
  }, [api, course])
  const names = namesOf(topics ?? [])

  return (
    <section className="add-material" aria-labelledby="add-title">
      <header className="page-header">
        <a
          className="link"
          href={href(subject && topic ? { page: 'topic', courseId, subject, topic } : { page: 'course', courseId })}
        >
          {subject && topic ? '← Back to the topic' : '← Back to the course'}
        </a>
        <h2 id="add-title">Add material{course ? ` to ${course.title}` : ''}</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {course && topics && (
        <div className="card">
          <UploadForm
            api={api}
            course={course.name}
            subject={subject}
            topic={topic}
            topicName={subject && topic ? `${names.subject(subject)} › ${names.topic(subject, topic)}` : undefined}
            onUploaded={(upload, { subject, topic, filename }) => {
              const broken = brokenReferences(filename, upload.broken_references)
              if (broken) leaveNotice(broken)
              navigate({ page: 'topic', courseId, subject, topic })
            }}
          />
        </div>
      )}
    </section>
  )
}
