import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Course, StudyApi, Subject } from '../api'
import { NewTopicForm } from '../components/NewTopicForm'
import { RenameForm } from '../components/RenameForm'
import { href, navigate } from '../router'

// a subject, before any of its topics
function NewSubjectForm({ api, course, onCreated }: { api: StudyApi; course: Course; onCreated: () => void }) {
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    try {
      await api.createSubject(course.name, name)
      onCreated()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card" aria-label="New subject" onSubmit={submit}>
      <label>
        Subject
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Distributed systems" required />
      </label>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <button type="submit">Create subject</button>
    </form>
  )
}


// what `renaming` is when it's the course's title being changed: no subject id has a space
const COURSE = 'the course'

/** A course: its subjects, by name; a subject's topics are on its own page. */
export function CoursePage({ api, courseId }: { api: StudyApi; courseId: string }) {
  const [course, setCourse] = useState<Course | null | undefined>(undefined)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [addingTopic, setAddingTopic] = useState(false)
  const [addingSubject, setAddingSubject] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  // what is being renamed: the course (COURSE) or a subject
  const [renaming, setRenaming] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  const load = useCallback(() => {
    if (!course) return
    api.subjects(course.name).then(setSubjects, (e: Error) => setError(e.message))
  }, [api, course])

  useEffect(load, [load])

  if (course === undefined) return <p className="note">Opening…</p>
  if (course === null) {
    return (
      <p role="alert" className="error">
        There's no such course. <a href={href({ page: 'courses' })}>Back to my courses</a>
      </p>
    )
  }

  const isOwner = course.role === 'owner'
  // only the student who created the course can delete it
  const isCreator = course.owner === api.student

  async function deleteCourse() {
    if (!course) return
    try {
      await api.deleteCourse(course.name)
      navigate({ page: 'courses' })
    } catch (e) {
      setConfirmingDelete(false)
      setError((e as Error).message)
    }
  }

  async function changeTitle(title: string) {
    if (!course) return
    setCourse({ ...course, ...(await api.changeTitle(course.name, title)) })
    setRenaming(null)
  }

  async function renameSubject(subject: string, name: string) {
    if (!course) return
    await api.renameSubject(course.name, subject, name)
    setRenaming(null)
    load()
  }

  return (
    <section className="course" aria-labelledby="course-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'courses' })}>
          ← My courses
        </a>
        <div className="title-row">
          <h2 id="course-title">{course.title}</h2>
          {isCreator && (
            <button
              type="button"
              className="link"
              aria-label={`Rename ${course.title}`}
              onClick={() => setRenaming(renaming === COURSE ? null : COURSE)}
            >
              Rename
            </button>
          )}
        </div>
        {renaming === COURSE && (
          <RenameForm
            name={course.title}
            label="Title"
            onRename={changeTitle}
            onCancel={() => setRenaming(null)}
          />
        )}
        {course.owner !== api.student && (
          <p className="note">
            Shared with you by {course.owner} as {course.role === 'owner' ? 'an owner' : 'a reader'}
          </p>
        )}
        <div className="actions page-actions">
          {isOwner && (
            <>
              <a className="button" href={href({ page: 'add', courseId: course.id, subject: '', topic: '' })}>
                Add material
              </a>
              <button type="button" className="link" onClick={() => setAddingSubject(!addingSubject)}>
                New subject
              </button>
              <button type="button" className="link" onClick={() => setAddingTopic(!addingTopic)}>
                New topic
              </button>
            </>
          )}
          <a className="link" href={href({ page: 'members', courseId: course.id })}>
            Members
          </a>
          {isCreator && !confirmingDelete && (
            <button type="button" className="link danger" onClick={() => setConfirmingDelete(true)}>
              Delete course
            </button>
          )}
        </div>
        {confirmingDelete && (
          <div className="card confirm" role="alertdialog" aria-label="Delete this course">
            <p>
              Delete {course.title} and everything in it? Its material, topics, notes, summaries, quizzes and
              conversations go for every member, and this cannot be undone.
            </p>
            <div className="actions">
              <button type="button" className="danger" onClick={deleteCourse}>
                Yes, delete {course.title}
              </button>
              <button type="button" className="link" onClick={() => setConfirmingDelete(false)}>
                Cancel
              </button>
            </div>
          </div>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {addingSubject && (
        <NewSubjectForm
          api={api}
          course={course}
          onCreated={() => {
            setAddingSubject(false)
            load()
          }}
        />
      )}

      {addingTopic && (
        <NewTopicForm
          api={api}
          course={course}
          onCreated={() => {
            setAddingTopic(false)
            load()
          }}
        />
      )}

      {subjects.length === 0 ? (
        <p className="note">This course has no material yet.</p>
      ) : (
        <ul className="topics subjects" aria-label="Subjects">
          {subjects.map(({ subject, name }) => (
            <li key={subject}>
              <section className="subject" aria-label={name}>
                <header className="topic-header">
                  <h3>
                    <a href={href({ page: 'subject', courseId: course.id, subject })}>{name}</a>
                  </h3>
                  {isOwner && (
                    <button
                      type="button"
                      className="link"
                      aria-label={`Rename ${name}`}
                      onClick={() => setRenaming(renaming === subject ? null : subject)}
                    >
                      Rename
                    </button>
                  )}
                </header>
                {renaming === subject && (
                  <RenameForm
                    name={name}
                    onRename={(newName) => renameSubject(subject, newName)}
                    onCancel={() => setRenaming(null)}
                  />
                )}
              </section>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
