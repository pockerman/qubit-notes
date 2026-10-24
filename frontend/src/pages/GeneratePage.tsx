import { useEffect, useState, type FormEvent } from 'react'
import type { Course, Generated, GeneratedKind, Material, StudyApi } from '../api'
import { href } from '../router'
import { WriteMaterialPage } from './WriteMaterialPage'

const KINDS: { kind: GeneratedKind; label: string }[] = [
  { kind: 'revision notes', label: 'Revision notes' },
  { kind: 'cheat sheet', label: 'Cheat sheet' },
  { kind: 'combined notes', label: 'Combined notes' },
  { kind: 'worked examples', label: 'Worked examples' },
]

type Props = {
  api: StudyApi
  courseId: string
  subject: string
  topic: string
  // the materials to generate from
  documentIds: string[]
}

/** The AI writing new material from materials of a topic: what to make, then the result in the editor, to save. */
export function GeneratePage({ api, courseId, subject, topic, documentIds }: Props) {
  const [materials, setMaterials] = useState<Material[]>([])
  const [kind, setKind] = useState<GeneratedKind | ''>('revision notes')
  const [instructions, setInstructions] = useState('')
  const [writing, setWriting] = useState(false)
  const [generated, setGenerated] = useState<Generated | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .courses()
      .then((courses) => {
        const course: Course | undefined = courses.find((c) => c.id === courseId)
        if (!course) throw new Error('There is no such course')
        return api.materials(course.name)
      })
      .then(
        (all) => setMaterials(all.filter((m) => documentIds.includes(m.document_id))),
        (e: Error) => setError(e.message),
      )
  }, [api, courseId, documentIds])

  async function generate(event: FormEvent) {
    event.preventDefault()
    setWriting(true)
    setError(null)
    try {
      setGenerated(await api.generate(courseId, documentIds, kind || null, instructions))
    } catch (e) {
      setError((e as Error).message)
      setWriting(false)
    }
  }

  if (generated) {
    return (
      <WriteMaterialPage
        api={api}
        courseId={courseId}
        subject={subject}
        topic={topic}
        initial={generated}
        chooseTopic
      />
    )
  }

  return (
    <section className="generate-material" aria-labelledby="generate-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'topic', courseId, subject, topic })}>
          ← Back to the topic
        </a>
        <h2 id="generate-title">
          Generate material from {subject} › {topic}
        </h2>
      </header>

      <form className="card editor" aria-label="Generate material" onSubmit={generate}>
        <p className="note">
          From {materials.map((m) => m.filename).join(', ') || 'the materials ticked'}. The AI writes from them alone,
          and cites the sections it draws on; nothing is saved until you save it.
        </p>
        <label>
          Kind
          <select value={kind} onChange={(e) => setKind(e.target.value as GeneratedKind | '')}>
            {KINDS.map(({ kind, label }) => (
              <option key={kind} value={kind}>
                {label}
              </option>
            ))}
            <option value="">Only my instructions</option>
          </select>
        </label>
        <label>
          Instructions
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            rows={3}
            placeholder="e.g. Five questions to test myself on assembly"
          />
        </label>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <div className="actions">
          <button type="submit" disabled={writing || (!kind && !instructions.trim())}>
            {writing ? 'Writing…' : 'Generate'}
          </button>
          {writing && (
            <span role="status" className="note">
              The AI is writing; this can take a minute
            </span>
          )}
        </div>
      </form>
    </section>
  )
}
