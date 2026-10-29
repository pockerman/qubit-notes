import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Collection, Paper, PaperDetails, StudyApi } from '../api'
import { Assistant } from '../components/Assistant'
import { Members } from '../components/Members'
import { href, navigate } from '../router'
import { STATUS_LABEL } from '../status'

// where a collection's papers are, in it: the assistant on this topic is the assistant on the whole collection
const PAPERS = { subject: 'papers', topic: 'papers' }
// the files a paper can be
const PAPER_FILES = '.pdf,.epub,.md,.txt'

/** "Ada Lovelace, Alan Turing · 2017 · arXiv": what is known of who wrote the paper, when and where. */
function byline(details: PaperDetails): string {
  return [details.authors.join(', '), details.year ?? '', details.venue].filter(Boolean).join(' · ')
}

type DetailsFormProps = {
  details: PaperDetails
  onSave: (details: PaperDetails) => Promise<void>
  onCancel: () => void
}

/** Changes a paper's details: its authors are written one after another, separated by commas. */
function DetailsForm({ details, onSave, onCancel }: DetailsFormProps) {
  const [title, setTitle] = useState(details.title)
  const [authors, setAuthors] = useState(details.authors.join(', '))
  const [year, setYear] = useState(details.year?.toString() ?? '')
  const [venue, setVenue] = useState(details.venue)
  const [doi, setDoi] = useState(details.doi)
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    const written = year.trim()
    if (written && !/^\d{4}$/.test(written)) {
      setError('A year is four digits, e.g. 2017')
      return
    }
    try {
      await onSave({
        title,
        authors: authors
          .split(',')
          .map((author) => author.trim())
          .filter(Boolean),
        year: written ? Number(written) : null,
        venue,
        doi,
      })
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card paper-details" aria-label="Paper details" onSubmit={submit}>
      <label>
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Authors
        <input value={authors} onChange={(e) => setAuthors(e.target.value)} placeholder="Ada Lovelace, Alan Turing" />
      </label>
      <div className="paper-details-row">
        <label>
          Year
          <input value={year} onChange={(e) => setYear(e.target.value)} inputMode="numeric" placeholder="2017" />
        </label>
        <label>
          Venue
          <input value={venue} onChange={(e) => setVenue(e.target.value)} placeholder="NeurIPS" />
        </label>
        <label>
          DOI
          <input value={doi} onChange={(e) => setDoi(e.target.value)} placeholder="10.1038/nature14236" />
        </label>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <button type="submit">Save details</button>
        <button type="button" className="link" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

/** A collection of papers: its papers with their details, adding to it, and the assistant on all of them. */
export function CollectionPage({ api, collectionId }: { api: StudyApi; collectionId: string }) {
  const [collection, setCollection] = useState<Collection | null | undefined>(undefined)
  const [papers, setPapers] = useState<Paper[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  // the paper whose details are being changed, by its document's id
  const [describing, setDescribing] = useState<string | null>(null)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [assistant, setAssistant] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.collection(collectionId).then(setCollection, (e: Error) => {
      setCollection(null)
      setError(e.message)
    })
  }, [api, collectionId])

  const load = useCallback(() => {
    api.papers(collectionId).then(setPapers, (e: Error) => setError(e.message))
  }, [api, collectionId])

  useEffect(load, [load])

  // a paper being processed is shown as ready once it is
  const processing = papers.some((p) => p.material.status === 'pending' || p.material.status === 'running')
  useEffect(() => {
    if (!processing) return
    const timer = setInterval(load, 1500)
    return () => clearInterval(timer)
  }, [processing, load])

  async function upload(event: FormEvent) {
    event.preventDefault()
    if (!file) return
    setUploading(true)
    try {
      await api.uploadPaper(collectionId, file)
      setFile(null)
      setError(null)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
    setUploading(false)
  }

  async function describe(paper: Paper, details: PaperDetails) {
    await api.describePaper(collectionId, paper.material.document_id, details)
    setDescribing(null)
    load()
  }

  async function remove(paper: Paper) {
    try {
      await api.deletePaper(collectionId, paper.material.document_id)
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function deleteCollection() {
    try {
      await api.deleteCollection(collectionId)
      navigate({ page: 'papers' })
    } catch (e) {
      setConfirmingDelete(false)
      setError((e as Error).message)
    }
  }

  if (collection === undefined) return <p className="note">Opening…</p>
  if (collection === null) {
    return (
      <p role="alert" className="error">
        There's no such collection. <a href={href({ page: 'papers' })}>Back to my papers</a>
      </p>
    )
  }
  const isOwner = collection.role === 'owner'
  // only the student who created the collection can delete it
  const isCreator = collection.owner === api.student
  const ready = papers.some((p) => p.material.status === 'completed')

  return (
    <section className="topic-page collection-page" aria-labelledby="collection-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'papers' })}>
          ← My papers
        </a>
        <h2 id="collection-title">{collection.title}</h2>
        <div className="actions page-actions">
          {isOwner && (
            <form className="upload-paper" aria-label="Add a paper" onSubmit={upload}>
              <label>
                Paper
                <input
                  type="file"
                  accept={PAPER_FILES}
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  // a new input once uploaded, so the same file can be chosen again
                  key={uploading ? 'uploading' : 'ready'}
                />
              </label>
              <button type="submit" disabled={!file || uploading}>
                {uploading ? 'Uploading…' : 'Add paper'}
              </button>
            </form>
          )}
          <a className="link" href={href({ page: 'collection-members', collectionId })}>
            Members
          </a>
          {isCreator && !confirmingDelete && (
            <button type="button" className="link danger" onClick={() => setConfirmingDelete(true)}>
              Delete collection
            </button>
          )}
          {ready && (
            <button type="button" aria-pressed={assistant} onClick={() => setAssistant(!assistant)}>
              AI
            </button>
          )}
        </div>
        {confirmingDelete && (
          <div className="card confirm" role="alertdialog" aria-label="Delete this collection">
            <p>
              Delete {collection.title} and its papers? Their notes, summaries and conversations go for every member,
              and this cannot be undone.
            </p>
            <div className="actions">
              <button type="button" className="danger" onClick={deleteCollection}>
                Yes, delete {collection.title}
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

      <div className={assistant ? 'topic-body with-assistant' : 'topic-body'}>
        <div>
          <h3>Papers</h3>
          {papers.length === 0 ? (
            <p className="note">No papers yet</p>
          ) : (
            <ul className="materials papers" aria-label="Papers">
              {papers.map((paper) => {
                const { material, details } = paper
                return (
                  <li key={material.document_id}>
                    <div className="paper">
                      {material.status === 'completed' ? (
                        <a
                          className="paper-title"
                          href={href({ page: 'paper', collectionId, documentId: material.document_id })}
                        >
                          {details.title}
                        </a>
                      ) : (
                        <span className="paper-title">{details.title}</span>
                      )}
                      <span className="note">
                        {[byline(details), material.filename].filter(Boolean).join(' · ')}
                      </span>
                      {material.status === 'failed' && material.error && (
                        <span className="note">{material.error}</span>
                      )}
                    </div>
                    {material.status !== 'completed' && (
                      <span
                        className={`badge ${material.status === 'failed' ? 'bad' : ''}`}
                        title={material.error ?? undefined}
                      >
                        {STATUS_LABEL[material.status]}
                      </span>
                    )}
                    {isOwner && (
                      <span className="topic-actions">
                        <button
                          type="button"
                          className="link"
                          aria-label={`Edit the details of ${details.title}`}
                          onClick={() =>
                            setDescribing(describing === material.document_id ? null : material.document_id)
                          }
                        >
                          Details
                        </button>
                        <button
                          type="button"
                          className="link"
                          aria-label={`Delete ${details.title}`}
                          onClick={() => remove(paper)}
                        >
                          Delete
                        </button>
                      </span>
                    )}
                    {describing === material.document_id && (
                      <DetailsForm
                        details={details}
                        onSave={(given) => describe(paper, given)}
                        onCancel={() => setDescribing(null)}
                      />
                    )}
                  </li>
                )
              })}
            </ul>
          )}
        </div>

        {assistant && (
          <Assistant
            key={collectionId}
            api={api}
            where={{ course_id: collectionId, ...PAPERS }}
            label={collection.title}
            onClose={() => setAssistant(false)}
          />
        )}
      </div>
    </section>
  )
}

/** Who a collection is shared with; any member sees them, only owners share it. */
export function CollectionMembersPage({ api, collectionId }: { api: StudyApi; collectionId: string }) {
  const [collection, setCollection] = useState<Collection | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.collection(collectionId).then(setCollection, (e: Error) => {
      setCollection(null)
      setError(e.message)
    })
  }, [api, collectionId])

  if (collection === undefined) return <p className="note">Opening…</p>
  if (collection === null) {
    return (
      <p role="alert" className="error">
        {error ?? "There's no such collection."} <a href={href({ page: 'papers' })}>Back to my papers</a>
      </p>
    )
  }
  return (
    <section className="course" aria-labelledby="members-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'collection', collectionId })}>
          ← {collection.title}
        </a>
        <h2 id="members-title">Members of {collection.title}</h2>
      </header>
      <Members api={api} course={collection} collection />
    </section>
  )
}
