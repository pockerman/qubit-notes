import { useEffect, useState, type FormEvent } from 'react'
import type { Course, StudyApi } from '../api'
import { RenameForm } from '../components/RenameForm'
import { slug } from '../names'
import { href, navigate } from '../router'

function NewCourseForm({ api, onCancel }: { api: StudyApi; onCancel: () => void }) {
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const stored = slug(name)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!stored) {
      setError('A course name needs at least one letter or digit')
      return
    }
    try {
      // known by its name, and shown by the title typed
      const course = await api.createCourse(stored, name)
      navigate({ page: 'course', courseId: course.id })
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card new-course" aria-label="New course" onSubmit={submit}>
      <label>
        Course name
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Computer science" autoFocus required />
      </label>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <button type="submit">Create course</button>
        <button type="button" className="link" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

/** The page a student lands on: their courses, and a way to create one. */
export function CoursesPage({ api }: { api: StudyApi }) {
  const [courses, setCourses] = useState<Course[] | null>(null)
  const [creating, setCreating] = useState(false)
  // the course whose title is being changed, by its id
  const [renaming, setRenaming] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(setCourses, (e: Error) => setError(e.message))
  }, [api])

  async function changeTitle(course: Course, title: string) {
    await api.changeTitle(course.name, title)
    setRenaming(null)
    setCourses(await api.courses())
  }

  return (
    <section className="courses-page" aria-labelledby="courses-title">
      <header className="page-header">
        <h2 id="courses-title">My courses</h2>
        {!creating && (
          <button type="button" onClick={() => setCreating(true)}>
            Create new course
          </button>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {creating && <NewCourseForm api={api} onCancel={() => setCreating(false)} />}

      {courses?.length === 0 && !creating && (
        <div className="empty card">
          <p>You have no courses yet.</p>
          <p className="note">Create a course, then add the material you study to it.</p>
        </div>
      )}

      {courses && courses.length > 0 && (
        <ul className="course-cards" aria-label="Courses">
          {courses.map((course) => (
            <li key={course.id}>
              <a className="card course-card" href={href({ page: 'course', courseId: course.id })}>
                <strong>{course.title}</strong>
                <span className="note">
                  {course.owner === api.student
                    ? 'yours'
                    : `shared by ${course.owner} · ${course.role === 'owner' ? 'owner' : 'reader'}`}
                </span>
              </a>
              {/* only its creator changes its title */}
              {course.owner === api.student && (
                <button
                  type="button"
                  className="link"
                  aria-label={`Rename ${course.title}`}
                  onClick={() => setRenaming(renaming === course.id ? null : course.id)}
                >
                  Rename
                </button>
              )}
              {renaming === course.id && (
                <RenameForm
                  name={course.title}
                  label="Title"
                  onRename={(title) => changeTitle(course, title)}
                  onCancel={() => setRenaming(null)}
                />
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
