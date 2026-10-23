import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import type { Course, Material, Mention, StudyApi, Topic } from '../api'
import { slug } from '../names'
import { takeNotice } from '../notices'
import { href, navigate } from '../router'

const STATUS_LABEL: Record<Material['status'], string> = {
  pending: 'processing',
  running: 'processing',
  completed: 'ready',
  failed: 'failed',
}

// subject to its topics, each with its materials: subjects sorted, topics in the order they're meant to be read, as
// listed. Topics stay when their material is deleted
function group(topics: Topic[], materials: Material[]): [string, [string, Material[]][]][] {
  const subjects = new Map<string, Map<string, Material[]>>()
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

// a topic in a subject the student names, or in `inSubject` when the course has it already
function NewTopicForm({
  api,
  course,
  inSubject,
  onCreated,
}: {
  api: StudyApi
  course: Course
  inSubject?: string
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
      await api.createTopic(course.name, slug(subject), slug(topic))
      onCreated()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card" aria-label={inSubject ? `New topic in ${inSubject}` : 'New topic'} onSubmit={submit}>
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

type Props = {
  api: StudyApi
  courseId: string
  // the topic to open the course at, e.g. one a reference refers to
  at?: { subject: string; topic: string }
}

export function CoursePage({ api, courseId, at }: Props) {
  const [course, setCourse] = useState<Course | null | undefined>(undefined)
  const [materials, setMaterials] = useState<Material[]>([])
  const [topics, setTopics] = useState<Topic[]>([])
  // the materials each topic is mentioned in, by "subject/topic"
  const [mentions, setMentions] = useState<Map<string, Mention[]>>(new Map())
  // e.g. that the material just saved has broken references
  const [notice] = useState(takeNotice)
  const target = useRef<HTMLElement | null>(null)
  const [addingTopic, setAddingTopic] = useState(false)
  // the subject a topic is being added to, from its own section
  const [addingTo, setAddingTo] = useState<string | null>(null)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  const load = useCallback(() => {
    if (!course) return
    Promise.all([api.materials(course.name), api.topics(course.name), api.mentions(course.name)]).then(
      ([m, t, mentioned]) => {
        setMaterials(m)
        setTopics(t)
        setMentions(new Map(mentioned.map((each) => [`${each.subject}/${each.topic}`, each.mentioned_in])))
      },
      (e: Error) => setError(e.message),
    )
  }, [api, course])

  useEffect(load, [load])

  // the topic the course was opened at is scrolled to, once it's shown
  const shown = topics.length > 0
  useEffect(() => {
    if (shown) target.current?.scrollIntoView({ block: 'start' })
  }, [shown, at?.subject, at?.topic])

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

  async function remove(material: Material) {
    try {
      await api.deleteMaterial(material)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const grouped = group(topics, materials)

  return (
    <section className="course" aria-labelledby="course-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'courses' })}>
          ← My courses
        </a>
        <h2 id="course-title">{course.name}</h2>
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
              Delete {course.name} and everything in it? Its material, topics, notes, summaries, quizzes and
              conversations go for every member, and this cannot be undone.
            </p>
            <div className="actions">
              <button type="button" className="danger" onClick={deleteCourse}>
                Yes, delete {course.name}
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
      {notice && (
        <p role="status" className="warning">
          {notice}
        </p>
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
        grouped.map(([subject, of]) => (
          <section key={subject} className="subject" aria-label={subject}>
            <header className="topic-header">
              <h3>{subject}</h3>
              {isOwner && (
                <button
                  type="button"
                  className="link"
                  aria-label={`Add a topic to ${subject}`}
                  onClick={() => setAddingTo(addingTo === subject ? null : subject)}
                >
                  Add topic
                </button>
              )}
            </header>
            {addingTo === subject && (
              <NewTopicForm
                api={api}
                course={course}
                inSubject={subject}
                onCreated={() => {
                  setAddingTo(null)
                  load()
                }}
              />
            )}
            {of.map(([topic, items], index) => {
              const targeted = at?.subject === subject && at?.topic === topic
              const mentionedIn = mentions.get(`${subject}/${topic}`) ?? []
              return (
                <section
                  key={topic}
                  ref={targeted ? target : undefined}
                  className={targeted ? 'topic targeted' : 'topic'}
                  aria-label={`${subject} › ${topic}`}
                  aria-current={targeted ? 'location' : undefined}
                >
                  <header className="topic-header">
                    <h4>{topic}</h4>
                    {isOwner && of.length > 1 && (
                      <span className="move">
                        <button
                          type="button"
                          className="link"
                          aria-label={`Move ${topic} up`}
                          disabled={index === 0}
                          onClick={() => move(subject, of.map(([t]) => t), index, -1)}
                        >
                          ↑
                        </button>
                        <button
                          type="button"
                          className="link"
                          aria-label={`Move ${topic} down`}
                          disabled={index === of.length - 1}
                          onClick={() => move(subject, of.map(([t]) => t), index, 1)}
                        >
                          ↓
                        </button>
                      </span>
                    )}
                    {isOwner && (
                      <>
                        <a
                          className="link"
                          href={href({ page: 'add', courseId: course.id, subject, topic })}
                          aria-label={`Add material to ${topic}`}
                        >
                          Add material
                        </a>
                        <a
                          className="link"
                          href={href({ page: 'write', courseId: course.id, subject, topic })}
                          aria-label={`Write material in ${topic}`}
                        >
                          Write material
                        </a>
                      </>
                    )}
                    {items.some((m) => m.kind === 'text' && m.status === 'completed') && (
                      <a className="link" href={href({ page: 'topic', courseId: course.id, subject, topic })}>
                        Study this topic
                      </a>
                    )}
                  </header>
                  {items.length === 0 ? (
                    <p className="note">No material yet</p>
                  ) : (
                    <ul>
                      {items.map((material) => (
                        <li key={material.document_id}>
                          {material.status === 'completed' ? (
                            <a
                              className="filename"
                              href={href({ page: 'material', courseId: course.id, documentId: material.document_id })}
                            >
                              {material.filename}
                            </a>
                          ) : (
                            <span className="filename">{material.filename}</span>
                          )}
                          <span
                            className={`badge ${material.status === 'failed' ? 'bad' : ''}`}
                            title={material.error ?? undefined}
                          >
                            {STATUS_LABEL[material.status]}
                          </span>
                          {material.status === 'failed' && material.error && (
                            <span className="note">{material.error}</span>
                          )}
                          {isOwner && (
                            <button
                              type="button"
                              className="link"
                              aria-label={`Delete ${material.filename}`}
                              onClick={() => remove(material)}
                            >
                              Delete
                            </button>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                  {mentionedIn.length > 0 && (
                    <p className="mentions note" aria-label={`Mentions of ${topic}`}>
                      Mentioned in{' '}
                      {mentionedIn.map((mention, i) => (
                        <span key={mention.document_id}>
                          {i > 0 && ', '}
                          <a href={href({ page: 'material', courseId: course.id, documentId: mention.document_id })}>
                            {mention.material}
                          </a>
                          {(mention.subject !== subject || mention.topic !== topic) &&
                            ` (${mention.subject === subject ? mention.topic : `${mention.subject} › ${mention.topic}`})`}
                        </span>
                      ))}
                    </p>
                  )}
                </section>
              )
            })}
          </section>
        ))
      )}
    </section>
  )
}
