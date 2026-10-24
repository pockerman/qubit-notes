import { useEffect, useState, type FormEvent } from 'react'
import type { Course, Generated, GeneratedKind, Material, StudyApi } from '../api'
import { href, navigate } from '../router'
import { STATUS_LABEL } from '../status'
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
}

/** The AI writing new material from materials of a topic: which, and what to make, then the result in the editor, to
 * save. */
export function GeneratePage({ api, courseId, subject, topic }: Props) {
  const [materials, setMaterials] = useState<Material[]>([])
  // the materials ticked to generate from, by document id
  const [ticked, setTicked] = useState<string[]>([])
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
        (all) => setMaterials(all.filter((m) => m.subject === subject && m.topic === topic)),
        (e: Error) => setError(e.message),
      )
  }, [api, courseId, subject, topic])

  function tick(material: Material, on: boolean) {
    setTicked(on ? [...ticked, material.document_id] : ticked.filter((id) => id !== material.document_id))
  }

  async function generate(event: FormEvent) {
    event.preventDefault()
    setWriting(true)
    setError(null)
    try {
      setGenerated(await api.generate(courseId, ticked, kind || null, instructions))
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
          Tick the materials to generate from. The AI writes from them alone, and cites the sections it draws on;
          nothing is saved until you save it.
        </p>
        <ul className="materials" aria-label="Materials to generate from">
          {materials.map((material) => {
            // only ready text can be generated from
            const usable = material.kind === 'text' && material.status === 'completed'
            return (
              <li key={material.document_id}>
                <label>
                  <input
                    type="checkbox"
                    aria-label={`Tick ${material.filename}`}
                    disabled={!usable || writing}
                    checked={ticked.includes(material.document_id)}
                    onChange={(e) => tick(material, e.target.checked)}
                  />{' '}
                  <span className="filename">{material.filename}</span>
                </label>
                {!usable && (
                  <span className="note">
                    {material.kind === 'video' ? 'a video, with no text' : STATUS_LABEL[material.status]}
                  </span>
                )}
              </li>
            )
          })}
        </ul>
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
          <button type="submit" disabled={writing || ticked.length === 0 || (!kind && !instructions.trim())}>
            {writing ? 'Writing…' : 'Generate'}
          </button>
          <button type="button" className="link" onClick={() => navigate({ page: 'topic', courseId, subject, topic })}>
            Cancel
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
