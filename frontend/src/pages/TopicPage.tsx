import { useCallback, useEffect, useState } from 'react'
import type { Course, Material, Mention, StudyApi } from '../api'
import { Assistant } from '../components/Assistant'
import { takeNotice } from '../notices'
import { href, navigate } from '../router'
import { STATUS_LABEL } from '../status'

type Props = { api: StudyApi; courseId: string; subject: string; topic: string }

/** A topic: its material, adding to it, the materials it is mentioned in, and the assistant on all of it. */
export function TopicPage({ api, courseId, subject, topic }: Props) {
  const [course, setCourse] = useState<Course | null | undefined>(undefined)
  const [materials, setMaterials] = useState<Material[]>([])
  const [mentions, setMentions] = useState<Mention[]>([])
  const [assistant, setAssistant] = useState(false)
  // the materials ticked to generate new material from, by document id
  const [ticked, setTicked] = useState<string[]>([])
  // e.g. that the material just saved has broken references
  const [notice] = useState(takeNotice)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.courses().then(
      (courses) => setCourse(courses.find((c) => c.id === courseId) ?? null),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId])

  const load = useCallback(() => {
    if (!course) return
    Promise.all([api.materials(course.name), api.mentions(course.name)]).then(
      ([all, mentioned]) => {
        setMaterials(all.filter((m) => m.subject === subject && m.topic === topic))
        setMentions(mentioned.find((t) => t.subject === subject && t.topic === topic)?.mentioned_in ?? [])
      },
      (e: Error) => setError(e.message),
    )
  }, [api, course, subject, topic])

  useEffect(load, [load])

  // material being processed is shown as ready once it is
  const processing = materials.some((m) => m.status === 'pending' || m.status === 'running')
  useEffect(() => {
    if (!processing) return
    const timer = setInterval(load, 1500)
    return () => clearInterval(timer)
  }, [processing, load])

  // moves a material one place up (-1) or down (+1) in the topic
  async function move(index: number, by: -1 | 1) {
    if (!course) return
    const order = materials.map((m) => m.filename)
    ;[order[index], order[index + by]] = [order[index + by], order[index]]
    try {
      setMaterials(await api.orderMaterials(course.name, subject, topic, order))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  function tick(material: Material, on: boolean) {
    setTicked(on ? [...ticked, material.document_id] : ticked.filter((id) => id !== material.document_id))
  }

  async function remove(material: Material) {
    try {
      await api.deleteMaterial(material)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  if (course === undefined) return <p className="note">Opening…</p>
  if (course === null) {
    return (
      <p role="alert" className="error">
        There's no such course. <a href={href({ page: 'courses' })}>Back to my courses</a>
      </p>
    )
  }
  const isOwner = course.role === 'owner'
  const ready = materials.some((m) => m.kind === 'text' && m.status === 'completed')

  return (
    <section className="topic-page" aria-labelledby="topic-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'course', courseId })}>
          ← Back to {course.name}
        </a>
        <h2 id="topic-title">
          {subject} › {topic}
        </h2>
        <div className="actions page-actions">
          {isOwner && (
            <>
              <a
                className="button"
                href={href({ page: 'add', courseId, subject, topic })}
                aria-label={`Add material to ${topic}`}
              >
                Add material
              </a>
              <a
                className="link"
                href={href({ page: 'write', courseId, subject, topic })}
                aria-label={`Write material in ${topic}`}
              >
                Write material
              </a>
            </>
          )}
          {ready && (
            <button type="button" aria-pressed={assistant} onClick={() => setAssistant(!assistant)}>
              AI
            </button>
          )}
        </div>
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

      <div className={assistant ? 'topic-body with-assistant' : 'topic-body'}>
        <div>
          <h3>Materials</h3>
          {materials.length === 0 ? (
            <p className="note">No material yet</p>
          ) : (
            <ul className="materials" aria-label="Materials">
              {materials.map((material, index) => (
                <li key={material.document_id}>
                  {isOwner && (
                    <input
                      type="checkbox"
                      aria-label={`Tick ${material.filename}`}
                      // only ready text can be generated from
                      disabled={material.kind !== 'text' || material.status !== 'completed'}
                      checked={ticked.includes(material.document_id)}
                      onChange={(e) => tick(material, e.target.checked)}
                    />
                  )}
                  {material.status === 'completed' ? (
                    <a
                      className="filename"
                      href={href({ page: 'material', courseId, documentId: material.document_id })}
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
                  {material.status === 'failed' && material.error && <span className="note">{material.error}</span>}
                  {isOwner && materials.length > 1 && (
                    <span className="topic-actions">
                      <button
                        type="button"
                        className="link"
                        aria-label={`Move ${material.filename} up`}
                        disabled={index === 0}
                        onClick={() => move(index, -1)}
                      >
                        ↑
                      </button>
                      <button
                        type="button"
                        className="link"
                        aria-label={`Move ${material.filename} down`}
                        disabled={index === materials.length - 1}
                        onClick={() => move(index, 1)}
                      >
                        ↓
                      </button>
                    </span>
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

          {isOwner && materials.length > 0 && (
            <p className="note">
              <button
                type="button"
                disabled={ticked.length === 0}
                onClick={() => navigate({ page: 'generate', courseId, subject, topic, documentIds: ticked })}
              >
                Generate material
              </button>{' '}
              {ticked.length === 0
                ? 'Tick materials for the AI to write new material from, such as revision notes.'
                : `from the ${ticked.length === 1 ? 'material' : `${ticked.length} materials`} ticked`}
            </p>
          )}

          {mentions.length > 0 && (
            <p className="mentions note" aria-label={`Mentions of ${topic}`}>
              Mentioned in{' '}
              {mentions.map((mention, i) => (
                <span key={mention.document_id}>
                  {i > 0 && ', '}
                  <a href={href({ page: 'material', courseId, documentId: mention.document_id })}>{mention.material}</a>
                  {(mention.subject !== subject || mention.topic !== topic) &&
                    ` (${mention.subject === subject ? mention.topic : `${mention.subject} › ${mention.topic}`})`}
                </span>
              ))}
            </p>
          )}
        </div>

        {assistant && (
          <Assistant
            key={`${courseId}/${subject}/${topic}`}
            api={api}
            where={{ course_id: courseId, subject, topic }}
            label={`${subject} › ${topic}`}
            onClose={() => setAssistant(false)}
          />
        )}
      </div>
    </section>
  )
}
