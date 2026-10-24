import { useCallback, useEffect, useState } from 'react'
import type { Course, Material, StudyApi, Subject, Topic } from '../api'
import { NewTopicForm } from '../components/NewTopicForm'
import { RenameForm } from '../components/RenameForm'
import { namesOf } from '../names'
import { href, navigate } from '../router'
import { topicStatus } from '../status'

// what `renaming` is when it's the subject being renamed: no topic id has a space
const SUBJECT = 'the subject'

/** A subject: its topics, in the order they're meant to be read, each with its status; a topic's material is on its
 * own page. */
export function SubjectPage({ api, courseId, subject }: { api: StudyApi; courseId: string; subject: string }) {
  const [course, setCourse] = useState<Course | null | undefined>(undefined)
  const [materials, setMaterials] = useState<Material[]>([])
  const [topics, setTopics] = useState<Topic[]>([])
  const [subjects, setSubjects] = useState<Subject[] | null>(null)
  // the topic being deleted, once its owner has asked to
  const [deletingTopic, setDeletingTopic] = useState<string | null>(null)
  const [addingTopic, setAddingTopic] = useState(false)
  // what is being renamed: the subject (SUBJECT) or one of its topics
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
        setMaterials(m.filter((material) => material.subject === subject))
        setTopics(t)
        setSubjects(s)
      },
      (e: Error) => setError(e.message),
    )
  }, [api, course, subject])

  useEffect(load, [load])

  // material being processed is shown as ready once it is
  const processing = materials.some((m) => m.status === 'pending' || m.status === 'running')
  useEffect(() => {
    if (!processing) return
    const timer = setInterval(load, 1500)
    return () => clearInterval(timer)
  }, [processing, load])

  if (course === undefined || (course && subjects === null && !error)) return <p className="note">Opening…</p>
  if (course === null) {
    return (
      <p role="alert" className="error">
        There's no such course. <a href={href({ page: 'courses' })}>Back to my courses</a>
      </p>
    )
  }
  const found = subjects?.find((s) => s.subject === subject)
  if (!found) {
    return (
      <p role="alert" className="error">
        {error ?? `${course.title} has no such subject.`}{' '}
        <a href={href({ page: 'course', courseId })}>Back to {course.title}</a>
      </p>
    )
  }

  const isOwner = course.role === 'owner'
  const names = namesOf(topics)
  const subjectName = found.name
  // the subject's topics, in their order, each with its materials
  const of: [string, Material[]][] = topics
    .filter((t) => t.subject === subject)
    .map((t) => [t.topic, materials.filter((m) => m.topic === t.topic)])

  // moves a topic one place up (-1) or down (+1) among the subject's topics
  async function move(order: string[], index: number, by: -1 | 1) {
    if (!course) return
    ;[order[index], order[index + by]] = [order[index + by], order[index]]
    try {
      setTopics(await api.orderTopics(course.name, subject, order))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function deleteTopic(topic: string) {
    if (!course) return
    setDeletingTopic(null)
    try {
      await api.deleteTopic(course.name, subject, topic)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function renameTopic(topic: string, name: string) {
    if (!course) return
    await api.renameTopic(course.name, subject, topic, name)
    setRenaming(null)
    load()
  }

  async function renameSubject(name: string) {
    if (!course) return
    setTopics(await api.renameSubject(course.name, subject, name))
    setRenaming(null)
    load()
  }

  async function deleteSubject() {
    if (!course) return
    try {
      await api.deleteSubject(course.name, subject)
      navigate({ page: 'course', courseId })
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <section className="subject-page" aria-labelledby="subject-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'course', courseId })}>
          ← Back to {course.title}
        </a>
        <div className="title-row">
          <h2 id="subject-title">{subjectName}</h2>
          {isOwner && (
            <button
              type="button"
              className="link"
              aria-label={`Rename ${subjectName}`}
              onClick={() => setRenaming(renaming === SUBJECT ? null : SUBJECT)}
            >
              Rename
            </button>
          )}
        </div>
        {renaming === SUBJECT && (
          <RenameForm name={subjectName} onRename={renameSubject} onCancel={() => setRenaming(null)} />
        )}
        {isOwner && (
          <div className="actions page-actions">
            <button
              type="button"
              className="link"
              aria-label={`Add a topic to ${subjectName}`}
              onClick={() => setAddingTopic(!addingTopic)}
            >
              Add topic
            </button>
            {of.length === 0 && (
              <button
                type="button"
                className="link danger"
                aria-label={`Delete ${subjectName}`}
                onClick={deleteSubject}
              >
                Delete
              </button>
            )}
          </div>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {addingTopic && (
        <NewTopicForm
          api={api}
          course={course}
          inSubject={subject}
          inSubjectName={subjectName}
          onCreated={() => {
            setAddingTopic(false)
            load()
          }}
        />
      )}

      {of.length === 0 && <p className="note">No topics yet</p>}
      <ol className="topics" aria-label={`Topics of ${subjectName}`}>
        {of.map(([topic, items], index) => {
          const status = topicStatus(items)
          const name = names.topic(subject, topic)
          return (
            <li key={topic}>
              <section className="topic" aria-label={`${subjectName} › ${name}`}>
                <header className="topic-header">
                  <h4>
                    <a href={href({ page: 'topic', courseId, subject, topic })}>{name}</a>
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
                            onClick={() =>
                              move(
                                of.map(([t]) => t),
                                index,
                                -1,
                              )
                            }
                          >
                            ↑
                          </button>
                          <button
                            type="button"
                            className="link"
                            aria-label={`Move ${name} down`}
                            disabled={index === of.length - 1}
                            onClick={() =>
                              move(
                                of.map(([t]) => t),
                                index,
                                1,
                              )
                            }
                          >
                            ↓
                          </button>
                        </>
                      )}
                      <button
                        type="button"
                        className="link"
                        aria-label={`Rename ${name}`}
                        onClick={() => setRenaming(renaming === topic ? null : topic)}
                      >
                        Rename
                      </button>
                      <button
                        type="button"
                        className="link danger"
                        aria-label={`Delete ${name}`}
                        onClick={() => setDeletingTopic(topic)}
                      >
                        Delete
                      </button>
                    </span>
                  )}
                </header>
                {renaming === topic && (
                  <RenameForm
                    name={name}
                    onRename={(newName) => renameTopic(topic, newName)}
                    onCancel={() => setRenaming(null)}
                  />
                )}
                {deletingTopic === topic && (
                  <div className="card confirm" role="alertdialog" aria-label={`Delete the topic ${name}`}>
                    <p>
                      {items.length === 0
                        ? `Delete ${name}? It has no material.`
                        : `Delete ${name} and its ${items.length === 1 ? 'material' : `${items.length} materials`}? ` +
                          'Their notes, summaries, quizzes and conversations go for every member, and this ' +
                          'cannot be undone.'}
                    </p>
                    <div className="actions">
                      <button type="button" className="danger" onClick={() => deleteTopic(topic)}>
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
}
