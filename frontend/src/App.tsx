import { useEffect, useMemo, useState } from 'react'
import { StudyApi, type Course } from './api'
import { PlatformStatus } from './components/PlatformStatus'
import { Reader } from './components/Reader'
import { SignIn } from './components/SignIn'
import { AddMaterialPage } from './pages/AddMaterialPage'
import { CoursePage } from './pages/CoursePage'
import { CoursesPage } from './pages/CoursesPage'
import { MembersPage } from './pages/MembersPage'
import { TopicPage } from './pages/TopicPage'
import { WriteMaterialPage } from './pages/WriteMaterialPage'
import { href, navigate, useRoute } from './router'

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

/** A material opened for reading, with whether the student may edit it. */
function MaterialPage({ api, courseId, documentId }: { api: StudyApi; courseId: string; documentId: string }) {
  const [course, setCourse] = useState<Course | null>(null)
  useEffect(() => {
    api.courses().then((courses) => setCourse(courses.find((c) => c.id === courseId) ?? null))
  }, [api, courseId])
  return (
    <Reader
      api={api}
      courseId={courseId}
      documentId={documentId}
      canEdit={course?.role === 'owner'}
      onClose={() => navigate({ page: 'course', courseId })}
    />
  )
}

function Pages({ api }: { api: StudyApi }) {
  const route = useRoute()
  switch (route.page) {
    case 'courses':
      return <CoursesPage api={api} />
    case 'course':
      return <CoursePage key={route.courseId} api={api} courseId={route.courseId} />
    case 'add':
      return <AddMaterialPage api={api} courseId={route.courseId} subject={route.subject} topic={route.topic} />
    case 'write':
      return <WriteMaterialPage api={api} courseId={route.courseId} subject={route.subject} topic={route.topic} />
    case 'members':
      return <MembersPage key={route.courseId} api={api} courseId={route.courseId} />
    case 'material':
      return <MaterialPage key={route.documentId} api={api} courseId={route.courseId} documentId={route.documentId} />
    case 'topic':
      return <TopicPage api={api} courseId={route.courseId} subject={route.subject} topic={route.topic} />
  }
}

export default function App() {
  const [student, setStudent] = useState<string | null>(storedStudent)
  const api = useMemo(() => (student ? new StudyApi(student) : null), [student])

  function signIn(name: string | null) {
    storeStudent(name)
    setStudent(name)
    navigate({ page: 'courses' })
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>
          <a href={href({ page: 'courses' })}>Study Assistant</a>
        </h1>
        {api && (
          <nav className="session" aria-label="Session">
            <a href={href({ page: 'courses' })}>My courses</a>
            <PlatformStatus api={api} />
            <span>Signed in as {api.student}</span>
            <button type="button" className="link" onClick={() => signIn(null)}>
              Sign out
            </button>
          </nav>
        )}
      </header>
      <main>{api ? <Pages key={api.student} api={api} /> : <SignIn onSignIn={signIn} />}</main>
    </div>
  )
}
