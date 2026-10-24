import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Course, Material, StudyApi, Subject, Topic } from '../api'
import { RenameForm } from '../components/RenameForm'
import { namesOf, slug } from '../names'
import { href, navigate } from '../router'
import { topicStatus } from '../status'

// subject to its topics, each with its materials: subjects sorted, topics in the order they're meant to be read, as
// listed. Subjects stay when their topics are deleted, and topics when their material is
function group(subjectIds: string[], topics: Topic[], materials: Material[]): [string, [string, Material[]][]][] {
  const subjects = new Map<string, Map<string, Material[]>>(subjectIds.map((s) => [s, new Map()]))
  const topicOf = (subject: string, topic: string) => {
    const of = subjects.get(subject) ?? new Map<string, Material[]>()
    subjects.set(subject, of)
    if (!of.has(topic)) of.set(topic, [])
    return of.get(topic)!
  }
  for (const t of topics) topicOf(t.subject, t.topic)
  for (const material of materials) topicOf(material.subject, material.topic).push(material)
  return [...subjects.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([subject, of]) => [subject, [...of.entries()]])
}

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

// a topic in a subject the student names, or in `inSubject` when the course has it already
function NewTopicForm({
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

// what `renaming` is when it's the course's title being changed: no subject or topic id has a space
const COURSE = 'the course'

/** A course: its subjects and their topics, in order, each with its status; a topic's material is on its own page. */
export function CoursePage({ api, courseId }: { api: StudyApi; courseId: string }) {
  const [course, setCourse] = useState<Course | null | undefined>(undefined)
  const [materials, setMaterials] = useState<Material[]>([])
  const [topics, setTopics] = useState<Topic[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  // the topic being deleted, once its owner has asked to, as "subject/topic"
  const [deletingTopic, setDeletingTopic] = useState<string | null>(null)
  const [addingTopic, setAddingTopic] = useState(false)
  const [addingSubject, setAddingSubject] = useState(false)
  // the subject a topic is being added to, from its own section
  const [addingTo, setAddingTo] = useState<string | null>(null)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  // what is being renamed: the course (COURSE), a subject ("subject") or a topic ("subject/topic")
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
    Promise.all([api.materials(course.name), api.topics(course.name), api.subjects(course.name)]).then(
      ([m, t, s]) => {
        setMaterials(m)
        setTopics(t)
        setSubjects(s)
      },
      (e: Error) => setError(e.message),
    )
  }, [api, course])

  useEffect(load, [load])

  // material being processed is shown as ready once it is
  const processing = materials.some((m) => m.status === 'pending' || m.status === 'running')
  useEffect(() => {
    if (!processing) return
    const timer = setInterval(load, 1500)
    return () => clearInterval(timer)
  }, [processing, load])

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

  // moves a topic one place up (-1) or down (+1) among its subject's topics
  async function move(subject: string, topics: string[], index: number, by: -1 | 1) {
    if (!course) return
    const order = [...topics]
    ;[order[index], order[index + by]] = [order[index + by], order[index]]
    try {
      setTopics(await api.orderTopics(course.name, subject, order))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function deleteTopic(subject: string, topic: string) {
    if (!course) return
    setDeletingTopic(null)
    try {
      await api.deleteTopic(course.name, subject, topic)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function renameTopic(subject: string, topic: string, name: string) {
    if (!course) return
    await api.renameTopic(course.name, subject, topic, name)
    setRenaming(null)
    load()
  }

  async function changeTitle(title: string) {
    if (!course) return
    setCourse({ ...course, ...(await api.changeTitle(course.name, title)) })
    setRenaming(null)
  }

  async function renameSubject(subject: string, name: string) {
    if (!course) return
    setTopics(await api.renameSubject(course.name, subject, name))
    setRenaming(null)
    load()
  }

  async function deleteSubject(subject: string) {
    if (!course) return
    try {
      await api.deleteSubject(course.name, subject)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const grouped = group(subjects.map((s) => s.subject), topics, materials)
  const names = namesOf(topics)
  const subjectNames = new Map(subjects.map((s) => [s.subject, s.name]))

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

      {grouped.length === 0 ? (
        <p className="note">This course has no material yet.</p>
      ) : (
        grouped.map(([subject, of]) => {
          const subjectName = subjectNames.get(subject) ?? names.subject(subject)
          return (
            <section key={subject} className="subject" aria-label={subjectName}>
              <header className="topic-header">
                <h3>{subjectName}</h3>
                {isOwner && (
                  <>
                    <button
                      type="button"
                      className="link"
                      aria-label={`Add a topic to ${subjectName}`}
                      onClick={() => setAddingTo(addingTo === subject ? null : subject)}
                    >
                      Add topic
                    </button>
                    <button
                      type="button"
                      className="link"
                      aria-label={`Rename ${subjectName}`}
                      onClick={() => setRenaming(renaming === subject ? null : subject)}
                    >
                      Rename
                    </button>
                    {of.length === 0 && (
                      <button
                        type="button"
                        className="link danger"
                        aria-label={`Delete ${subjectName}`}
                        onClick={() => deleteSubject(subject)}
                      >
                        Delete
                      </button>
                    )}
                  </>
                )}
              </header>
              {renaming === subject && (
                <RenameForm
                  name={subjectName}
                  onRename={(name) => renameSubject(subject, name)}
                  onCancel={() => setRenaming(null)}
                />
              )}
              {addingTo === subject && (
                <NewTopicForm
                  api={api}
                  course={course}
                  inSubject={subject}
                  inSubjectName={subjectName}
                  onCreated={() => {
                    setAddingTo(null)
                    load()
                  }}
                />
              )}
              {of.length === 0 && <p className="note">No topics yet</p>}
              <ol className="topics" aria-label={`Topics of ${subjectName}`}>
                {of.map(([topic, items], index) => {
                  const status = topicStatus(items)
                  const deleting = deletingTopic === `${subject}/${topic}`
                  const name = names.topic(subject, topic)
                  return (
                    <li key={topic}>
                      <section className="topic" aria-label={`${subjectName} › ${name}`}>
                        <header className="topic-header">
                          <h4>
                            <a href={href({ page: 'topic', courseId: course.id, subject, topic })}>{name}</a>
                          </h4>
                          <span className={`badge ${status.bad ? 'bad' : ''}`} aria-label={`Status of ${name}`}>
                            {status.label}
                          </span>
                          {isOwner && (
                            <span className="topic-actions">
                              {of.length > 1 && (
                                <>
                                  <button
                                    type="button"
                                    className="link"
                                    aria-label={`Move ${name} up`}
                                    disabled={index === 0}
                                    onClick={() => move(subject, of.map(([t]) => t), index, -1)}
                                  >
                                    ↑
                                  </button>
                                  <button
                                    type="button"
                                    className="link"
                                    aria-label={`Move ${name} down`}
                                    disabled={index === of.length - 1}
                                    onClick={() => move(subject, of.map(([t]) => t), index, 1)}
                                  >
                                    ↓
                                  </button>
                                </>
                              )}
                              <button
                                type="button"
                                className="link"
                                aria-label={`Rename ${name}`}
                                onClick={() => {
                                  const key = `${subject}/${topic}`
                                  setRenaming(renaming === key ? null : key)
                                }}
                              >
                                Rename
                              </button>
                              <button
                                type="button"
                                className="link danger"
                                aria-label={`Delete ${name}`}
                                onClick={() => setDeletingTopic(`${subject}/${topic}`)}
                              >
                                Delete
                              </button>
                            </span>
                          )}
                        </header>
                        {renaming === `${subject}/${topic}` && (
                          <RenameForm
                            name={name}
                            onRename={(newName) => renameTopic(subject, topic, newName)}
                            onCancel={() => setRenaming(null)}
                          />
                        )}
                        {deleting && (
                          <div className="card confirm" role="alertdialog" aria-label={`Delete the topic ${name}`}>
                            <p>
                              {items.length === 0
                                ? `Delete ${name}? It has no material.`
                                : `Delete ${name} and its ${items.length === 1 ? 'material' : `${items.length} materials`}? ` +
                                  'Their notes, summaries, quizzes and conversations go for every member, and this ' +
                                  'cannot be undone.'}
                            </p>
                            <div className="actions">
                              <button type="button" className="danger" onClick={() => deleteTopic(subject, topic)}>
                                Yes, delete {name}
                              </button>
                              <button type="button" className="link" onClick={() => setDeletingTopic(null)}>
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}
                      </section>
                    </li>
                  )
                })}
              </ol>
            </section>
          )
        })
      )}
    </section>
  )
}
