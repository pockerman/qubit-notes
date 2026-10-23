import { useEffect, useState } from 'react'
import type { Material, Section, StudyApi, Topic } from '../api'
import { referenceTo } from '../references'

const WHOLE = ''

/** How references are written, beside the editor; docs/references.md has the rest. */
function ReferenceHelp({ onClose }: { onClose: () => void }) {
  return (
    <section className="reference-help card" aria-label="How references work">
      <p>Refer to another part of the course with its path in double brackets, starting at the subject:</p>
      <table>
        <thead>
          <tr>
            <th>To refer to</th>
            <th>Write</th>
            <th>Shown as</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>a topic</td>
            <td>
              <code>[[numerical-methods/finite-elements]]</code>
            </td>
            <td>finite-elements</td>
          </tr>
          <tr>
            <td>a material</td>
            <td>
              <code>[[numerical-methods/finite-elements/fem-notes.md]]</code>
            </td>
            <td>fem-notes.md</td>
          </tr>
          <tr>
            <td>a section</td>
            <td>
              <code>[[numerical-methods/finite-elements/fem-notes.md#2 Assembly]]</code>
            </td>
            <td>2 Assembly</td>
          </tr>
          <tr>
            <td>with a label</td>
            <td>
              <code>[[numerical-methods/finite-elements|the FEM topic]]</code>
            </td>
            <td>the FEM topic</td>
          </tr>
        </tbody>
      </table>
      <ul>
        <li>A label follows a "|". In a table, write it "\|".</li>
        <li>A section is named by its heading, without the # marks.</li>
        <li>
          A reference to something the course doesn't have is broken: it's struck through, and you're told when you
          save.
        </li>
        <li>
          Text in code, such as <code>`[[subject/topic]]`</code>, is not a reference.
        </li>
      </ul>
      <button type="button" className="link" onClick={onClose}>
        Close
      </button>
    </section>
  )
}

type Props = {
  api: StudyApi
  courseId: string
  onInsert: (reference: string) => void
}

/** Picks a topic of the course, or one of its materials, or a section of that, to refer to in the text. */
export function AddReference({ api, courseId, onInsert }: Props) {
  const [adding, setAdding] = useState(false)
  const [helping, setHelping] = useState(false)
  const [topics, setTopics] = useState<Topic[]>([])
  const [materials, setMaterials] = useState<Material[]>([])
  const [sections, setSections] = useState<Section[]>([])
  const [topic, setTopic] = useState(WHOLE)
  const [material, setMaterial] = useState(WHOLE)
  const [section, setSection] = useState(WHOLE)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!adding) return
    api
      .courses()
      .then((courses) => {
        const course = courses.find((c) => c.id === courseId)
        if (!course) throw new Error('There is no such course')
        return Promise.all([api.topics(course.name), api.materials(course.name)])
      })
      .then(
        ([t, m]) => {
          setTopics(t)
          setMaterials(m)
        },
        (e: Error) => setError(e.message),
      )
  }, [api, courseId, adding])

  const [subjectOf, topicOf] = topic.split('/')
  const inTopic = materials.filter((m) => m.subject === subjectOf && m.topic === topicOf)
  const picked = inTopic.find((m) => m.document_id === material)

  useEffect(() => {
    setSections([])
    setSection(WHOLE)
    if (!picked || picked.kind !== 'text' || picked.status !== 'completed') return
    api.openMaterial(courseId, picked.document_id).then(
      (opened) => setSections(opened.sections.filter((s) => s.title)),
      (e: Error) => setError(e.message),
    )
  }, [api, courseId, picked])

  function close() {
    setAdding(false)
    setTopic(WHOLE)
    setMaterial(WHOLE)
    setSection(WHOLE)
    setError(null)
  }

  if (!adding) {
    return (
      <>
        <p className="note">
          <button type="button" className="link" onClick={() => setAdding(true)}>
            Add reference
          </button>{' '}
          to a topic, a material or a section of the course, written <code>[[subject/topic]]</code>.{' '}
          <button type="button" className="link" aria-expanded={helping} onClick={() => setHelping(!helping)}>
            How references work
          </button>
        </p>
        {helping && <ReferenceHelp onClose={() => setHelping(false)} />}
      </>
    )
  }
  return (
    <div className="add-reference" role="group" aria-label="Add a reference">
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <label>
        Topic
        <select
          value={topic}
          onChange={(e) => {
            setTopic(e.target.value)
            setMaterial(WHOLE)
          }}
        >
          <option value={WHOLE}>Choose a topic</option>
          {topics.map((t) => (
            <option key={`${t.subject}/${t.topic}`} value={`${t.subject}/${t.topic}`}>
              {t.subject} › {t.topic}
            </option>
          ))}
        </select>
      </label>
      {topic && inTopic.length > 0 && (
        <label>
          Material
          <select value={material} onChange={(e) => setMaterial(e.target.value)}>
            <option value={WHOLE}>The whole topic</option>
            {inTopic.map((m) => (
              <option key={m.document_id} value={m.document_id}>
                {m.filename}
              </option>
            ))}
          </select>
        </label>
      )}
      {picked && sections.length > 0 && (
        <label>
          Section
          <select value={section} onChange={(e) => setSection(e.target.value)}>
            <option value={WHOLE}>The whole material</option>
            {sections.map((s) => (
              <option key={s.position} value={s.title}>
                {s.title}
              </option>
            ))}
          </select>
        </label>
      )}
      <div className="actions">
        <button
          type="button"
          disabled={!topic}
          onClick={() => {
            onInsert(referenceTo(subjectOf, topicOf, picked?.filename, section || undefined))
            close()
          }}
        >
          Insert
        </button>
        <button type="button" className="link" onClick={close}>
          Cancel
        </button>
      </div>
    </div>
  )
}
