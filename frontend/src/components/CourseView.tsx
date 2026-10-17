import { useCallback, useEffect, useState } from 'react'
import type { Course, Material, StudyApi } from '../api'
import { Members } from './Members'
import { UploadForm } from './UploadForm'

const STATUS_LABEL: Record<Material['status'], string> = {
  pending: 'processing',
  running: 'processing',
  completed: 'ready',
  failed: 'failed',
}

// subject to topic to materials, each level sorted
function group(materials: Material[]): [string, [string, Material[]][]][] {
  const subjects = new Map<string, Map<string, Material[]>>()
  for (const material of materials) {
    const topics = subjects.get(material.subject) ?? new Map<string, Material[]>()
    topics.set(material.topic, [...(topics.get(material.topic) ?? []), material])
    subjects.set(material.subject, topics)
  }
  return [...subjects.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([subject, topics]) => [subject, [...topics.entries()].sort(([a], [b]) => a.localeCompare(b))])
}

type Props = {
  api: StudyApi
  course: Course
  // reloads the material when it changes
  version: number
  // the course list changed, e.g. after an upload
  onChanged: () => void
  onOpen: (material: Material) => void
}

export function CourseView({ api, course, version, onChanged, onOpen }: Props) {
  const [materials, setMaterials] = useState<Material[]>([])
  const [error, setError] = useState<string | null>(null)
  const isOwner = course.role === 'owner'

  const load = useCallback(() => {
    api.materials(course.name).then(setMaterials, (e: Error) => setError(e.message))
  }, [api, course.name])

  useEffect(() => {
    load()
  }, [load, version])

  async function remove(material: Material) {
    try {
      await api.deleteMaterial(material)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <section className="course" aria-labelledby="course-title">
      <header>
        <h2 id="course-title">{course.name}</h2>
        {course.owner !== api.student && (
          <p className="note">
            Shared with you by {course.owner} as {course.role === 'owner' ? 'an owner' : 'a reader'}
          </p>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {materials.length === 0 ? (
        <p className="note">No material yet.</p>
      ) : (
        group(materials).map(([subject, topics]) => (
          <section key={subject} className="subject" aria-label={subject}>
            <h3>{subject}</h3>
            {topics.map(([topic, items]) => (
              <section key={topic} className="topic" aria-label={`${subject} › ${topic}`}>
                <h4>{topic}</h4>
                <ul>
                  {items.map((material) => (
                    <li key={material.document_id}>
                      {material.status === 'completed' ? (
                        <button type="button" className="link filename" onClick={() => onOpen(material)}>
                          {material.filename}
                        </button>
                      ) : (
                        <span className="filename">{material.filename}</span>
                      )}
                      <span className={`badge ${material.status === 'failed' ? 'bad' : ''}`}>
                        {STATUS_LABEL[material.status]}
                      </span>
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
              </section>
            ))}
          </section>
        ))
      )}

      {isOwner && (
        <details className="card">
          <summary>Upload to {course.name}</summary>
          <UploadForm
            api={api}
            course={course.name}
            onUploaded={() => {
              load()
              onChanged()
            }}
          />
        </details>
      )}

      <Members api={api} course={course} />
    </section>
  )
}
