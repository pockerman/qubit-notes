import { useEffect, useState, type FormEvent } from 'react'
import type { Collection, StudyApi } from '../api'
import { RenameForm } from '../components/RenameForm'
import { slug } from '../names'
import { href, navigate } from '../router'

function NewCollectionForm({ api, onCancel }: { api: StudyApi; onCancel: () => void }) {
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const stored = slug(name)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!stored) {
      setError('A collection name needs at least one letter or digit')
      return
    }
    try {
      // known by its name, and shown by the title typed
      const collection = await api.createCollection(stored, name)
      navigate({ page: 'collection', collectionId: collection.id })
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card new-course" aria-label="New collection" onSubmit={submit}>
      <label>
        Collection name
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Reinforcement learning"
          autoFocus
          required
        />
      </label>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <button type="submit">Create collection</button>
        <button type="button" className="link" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

/** The student's collections of papers, apart from their courses, and a way to create one. */
export function PapersPage({ api }: { api: StudyApi }) {
  const [collections, setCollections] = useState<Collection[] | null>(null)
  const [creating, setCreating] = useState(false)
  // the collection whose title is being changed, by its id
  const [renaming, setRenaming] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.collections().then(setCollections, (e: Error) => setError(e.message))
  }, [api])

  async function changeTitle(collection: Collection, title: string) {
    await api.changeCollectionTitle(collection.id, title)
    setRenaming(null)
    setCollections(await api.collections())
  }

  return (
    <section className="courses-page" aria-labelledby="papers-title">
      <header className="page-header">
        <h2 id="papers-title">My papers</h2>
        {!creating && (
          <button type="button" onClick={() => setCreating(true)}>
            Create new collection
          </button>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {creating && <NewCollectionForm api={api} onCancel={() => setCreating(false)} />}

      {collections?.length === 0 && !creating && (
        <div className="empty card">
          <p>You have no collections of papers yet.</p>
          <p className="note">Create a collection, then add the papers you read to it.</p>
        </div>
      )}

      {collections && collections.length > 0 && (
        <ul className="course-cards" aria-label="Collections">
          {collections.map((collection) => (
            <li key={collection.id}>
              <a className="card course-card" href={href({ page: 'collection', collectionId: collection.id })}>
                <strong>{collection.title}</strong>
                <span className="note">
                  {collection.papers === 1 ? '1 paper' : `${collection.papers} papers`} ·{' '}
                  {collection.owner === api.student
                    ? 'yours'
                    : `shared by ${collection.owner} · ${collection.role === 'owner' ? 'owner' : 'reader'}`}
                </span>
              </a>
              {/* only its creator changes its title */}
              {collection.owner === api.student && (
                <button
                  type="button"
                  className="link"
                  aria-label={`Rename ${collection.title}`}
                  onClick={() => setRenaming(renaming === collection.id ? null : collection.id)}
                >
                  Rename
                </button>
              )}
              {renaming === collection.id && (
                <RenameForm
                  name={collection.title}
                  label="Title"
                  onRename={(title) => changeTitle(collection, title)}
                  onCancel={() => setRenaming(null)}
                />
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
