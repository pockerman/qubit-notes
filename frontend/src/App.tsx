import { useCallback, useEffect, useMemo, useState } from 'react'
import { StudyApi, type Course } from './api'
import { CourseView } from './components/CourseView'
import { PlatformStatus } from './components/PlatformStatus'
import { SignIn } from './components/SignIn'
import { UploadForm } from './components/UploadForm'

const STUDENT_KEY = 'study-assistant.student'

function storedStudent(): string | null {
  try {
    return localStorage.getItem(STUDENT_KEY)
  } catch {
    return null
  }
}

function storeStudent(student: string | null) {
  try {
    if (student) localStorage.setItem(STUDENT_KEY, student)
    else localStorage.removeItem(STUDENT_KEY)
  } catch {
    // the student signs in again next time
  }
}

function Courses({ api }: { api: StudyApi }) {
  const [courses, setCourses] = useState<Course[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  // bumped when material changes outside the open course's view, so it reloads
  const [version, setVersion] = useState(0)

  const load = useCallback(() => {
    api.courses().then(setCourses, (e: Error) => setError(e.message))
  }, [api])

  useEffect(load, [load])

  const course = courses.find((c) => c.id === selected) ?? null

  return (
    <div className="layout">
      <nav aria-label="Courses" className="sidebar">
        <h2>Courses</h2>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {courses.length === 0 ? (
          <p className="note">No courses yet</p>
        ) : (
          <ul>
            {courses.map((c) => (
              <li key={c.id}>
                <button
                  type="button"
                  className={c.id === selected ? 'course-link selected' : 'course-link'}
                  aria-current={c.id === selected ? 'page' : undefined}
                  onClick={() => setSelected(c.id)}
                >
                  {c.name}
                  {c.owner !== api.student && <small> · {c.owner}</small>}
                </button>
              </li>
            ))}
          </ul>
        )}

        <section className="card" aria-labelledby="add-material-title">
          <h3 id="add-material-title">Add material</h3>
          <UploadForm
            api={api}
            onUploaded={(courseId) => {
              load()
              setSelected(courseId)
              setVersion((v) => v + 1)
            }}
          />
        </section>
      </nav>

      <main>
        {course ? (
          <CourseView key={course.id} api={api} course={course} version={version} onChanged={load} />
        ) : (
          <p className="note">Choose a course.</p>
        )}
      </main>
    </div>
  )
}

export default function App() {
  const [student, setStudent] = useState<string | null>(storedStudent)
  const api = useMemo(() => (student ? new StudyApi(student) : null), [student])

  function signIn(name: string | null) {
    storeStudent(name)
    setStudent(name)
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>Study Assistant</h1>
        {api && (
          <div className="session">
            <PlatformStatus api={api} />
            <span>Signed in as {api.student}</span>
            <button type="button" className="link" onClick={() => signIn(null)}>
              Sign out
            </button>
          </div>
        )}
      </header>
      {api ? <Courses key={api.student} api={api} /> : <SignIn onSignIn={signIn} />}
    </div>
  )
}
