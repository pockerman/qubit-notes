import { useEffect, useState } from 'react'
import type { Course, StudyApi } from '../api'
import { Members } from '../components/Members'
import { href } from '../router'

/** Who a course is shared with; any member sees them, only owners share it. */
export function MembersPage({ api, courseId }: { api: StudyApi; courseId: string }) {
  const [course, setCourse] = useState<Course | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  if (error) {
    return (
      <p role="alert" className="error">
        {error}
      </p>
    )
  }
  if (course === undefined) return <p className="note">Opening…</p>
  if (course === null) {
    return (
      <p role="alert" className="error">
        There's no such course. <a href={href({ page: 'courses' })}>Back to my courses</a>
      </p>
    )
  }

  return (
    <section className="course" aria-labelledby="members-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'course', courseId: course.id })}>
          ← {course.title}
        </a>
        <h2 id="members-title">Members of {course.title}</h2>
      </header>
      <Members api={api} course={course} />
    </section>
  )
}
