import { useEffect, useMemo, useState } from 'react'
import { authConfig, StudyApi, type Course } from './api'
import {
  cognitoIdentity,
  cognitoTokens,
  nameIdentity,
  startCognitoSignIn,
  storedStudent,
  type AuthConfig,
  type Identity,
} from './auth'
import { NavigationMenu } from './components/NavigationMenu'
import { PlatformStatus } from './components/PlatformStatus'
import { Reader } from './components/Reader'
import { SignIn } from './components/SignIn'
import { AddMaterialPage } from './pages/AddMaterialPage'
import { CoursePage } from './pages/CoursePage'
import { CoursesPage } from './pages/CoursesPage'
import { GeneratePage } from './pages/GeneratePage'
import { MembersPage } from './pages/MembersPage'
import { SettingsPage } from './pages/SettingsPage'
import { SubjectPage } from './pages/SubjectPage'
import { TopicPage } from './pages/TopicPage'
import { WriteMaterialPage } from './pages/WriteMaterialPage'
import { href, navigate, useRoute } from './router'

// who is signed in when the app opens: started once, as React may run an effect twice
let opening: Promise<{ config: AuthConfig; identity: Identity | null }> | null = null

function openSession(onSignOut: () => void) {
  opening ??= authConfig().then(async (config) => {
    if (config.auth === 'name') {
      const student = storedStudent()
      return { config, identity: student ? nameIdentity(student, onSignOut) : null }
    }
    const tokens = await cognitoTokens(config.cognito)
    if (!tokens) await startCognitoSignIn(config.cognito)
    return { config, identity: tokens ? cognitoIdentity(config.cognito, tokens) : null }
  })
  return opening
}

type MaterialPageProps = { api: StudyApi; courseId: string; documentId: string; section?: number }

/** A material opened for reading, at a section if one is given, with whether the student may edit it. */
function MaterialPage({ api, courseId, documentId, section }: MaterialPageProps) {
  const [course, setCourse] = useState<Course | null>(null)
  useEffect(() => {
    api.courses().then((courses) => setCourse(courses.find((c) => c.id === courseId) ?? null))
  }, [api, courseId])
  return (
    <Reader
      api={api}
      courseId={courseId}
      documentId={documentId}
      section={section}
      canEdit={course?.role === 'owner'}
      onClose={(material) =>
        navigate(
          material
            ? { page: 'topic', courseId, subject: material.subject, topic: material.topic }
            : { page: 'course', courseId },
        )
      }
    />
  )
}

function Pages({ api }: { api: StudyApi }) {
  const route = useRoute()
  switch (route.page) {
    case 'courses':
      return <CoursesPage api={api} />
    case 'settings':
      return <SettingsPage api={api} />
    case 'course':
      return <CoursePage key={route.courseId} api={api} courseId={route.courseId} />
    case 'subject':
      return (
        <SubjectPage
          key={`${route.courseId}/${route.subject}`}
          api={api}
          courseId={route.courseId}
          subject={route.subject}
        />
      )
    case 'add':
      return <AddMaterialPage api={api} courseId={route.courseId} subject={route.subject} topic={route.topic} />
    case 'write':
      return <WriteMaterialPage api={api} courseId={route.courseId} subject={route.subject} topic={route.topic} />
    case 'generate':
      return <GeneratePage api={api} courseId={route.courseId} subject={route.subject} topic={route.topic} />
    case 'members':
      return <MembersPage key={route.courseId} api={api} courseId={route.courseId} />
    case 'material':
      return (
        <MaterialPage
          key={`${route.documentId}:${route.section ?? ''}`}
          api={api}
          courseId={route.courseId}
          documentId={route.documentId}
          section={route.section}
        />
      )
    case 'topic':
      return (
        <TopicPage
          key={`${route.courseId}/${route.subject}/${route.topic}`}
          api={api}
          courseId={route.courseId}
          subject={route.subject}
          topic={route.topic}
        />
      )
  }
}

export default function App() {
  const [config, setConfig] = useState<AuthConfig | null>(null)
  const [identity, setIdentity] = useState<Identity | null>(null)
  const [error, setError] = useState<string | null>(null)
  const api = useMemo(() => (identity ? new StudyApi(identity) : null), [identity])

  useEffect(() => {
    openSession(() => setIdentity(null)).then(
      (opened) => {
        setConfig(opened.config)
        setIdentity(opened.identity)
      },
      (e: Error) => setError(e.message),
    )
  }, [])

  function signIn(name: string) {
    setIdentity(nameIdentity(name, () => setIdentity(null)))
    navigate({ page: 'courses' })
  }

  function signOut() {
    identity?.signOut()
    navigate({ page: 'courses' })
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <h1>
            <a href={href({ page: 'courses' })}>Qubit Notes</a>
          </h1>
          {api && <PlatformStatus api={api} />}
        </div>
        {api && (
          <nav className="session" aria-label="Session">
            <span>Signed in as {api.student}</span>
            <NavigationMenu onSignOut={signOut} />
          </nav>
        )}
      </header>
      <main>
        {api ? (
          <Pages key={api.student} api={api} />
        ) : error ? (
          <p role="alert" className="error">
            {error}
          </p>
        ) : config?.auth === 'name' ? (
          <SignIn onSignIn={signIn} />
        ) : (
          <p className="note">Signing in…</p>
        )}
      </main>
    </div>
  )
}
