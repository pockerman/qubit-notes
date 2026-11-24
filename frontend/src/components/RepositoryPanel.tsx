import { useEffect, useState, type FormEvent } from 'react'
import type { Pushed, StudyApi, SubjectRepository } from '../api'

type Props = {
  api: StudyApi
  // the course's name, as the API takes it
  course: string
  subject: string
  subjectName: string
}

// where GitHub gives fine-grained tokens
const NEW_TOKEN = 'https://github.com/settings/personal-access-tokens/new'

function sentence(message: string): string {
  return message.charAt(0).toUpperCase() + message.slice(1)
}

function files(count: number): string {
  return count === 1 ? '1 file' : `${count} files`
}

/** what a push did, e.g. "wrote 1 file and removed 1" */
function didWhat(pushed: Pushed): string {
  const wrote = `wrote ${files(pushed.written.length)}`
  return pushed.removed.length ? `${wrote} and removed ${pushed.removed.length}` : wrote
}

function when(at: string): string {
  const date = new Date(at)
  return Date.now() - date.getTime() < 60_000 ? 'just now' : date.toLocaleString()
}

/** The GitHub repository the student pushes a subject to, as they see it: connecting it, pushing to it, and
 * disconnecting it (features/ui_subject_repository.feature). */
export function RepositoryPanel({ api, course, subject, subjectName }: Props) {
  // undefined while it's asked for
  const [connection, setConnection] = useState<SubjectRepository | undefined>(undefined)
  const [repository, setRepository] = useState('')
  const [token, setToken] = useState('')
  const [connecting, setConnecting] = useState(false)
  const [pushing, setPushing] = useState(false)
  const [pushed, setPushed] = useState<Pushed | null>(null)
  const [disconnecting, setDisconnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.repository(course, subject).then(setConnection, (e: Error) => setError(sentence(e.message)))
  }, [api, course, subject])

  async function connect(event: FormEvent) {
    event.preventDefault()
    setConnecting(true)
    setError(null)
    try {
      setConnection(await api.connectRepository(course, subject, repository.trim(), token))
      setPushed(null)
    } catch (e) {
      setError(sentence((e as Error).message))
    }
    // the token isn't kept in the page, whether or not it was taken
    setToken('')
    setConnecting(false)
  }

  async function push() {
    setPushing(true)
    setError(null)
    setPushed(null)
    try {
      const done = await api.pushRepository(course, subject)
      setPushed(done)
      if (done.pushed) {
        setConnection(
          (c) =>
            c && {
              ...c,
              pushed_at: done.pushed_at,
              commit_sha: done.commit_sha,
              commit_url: done.commit_url,
            },
        )
      }
    } catch (e) {
      setError(sentence((e as Error).message))
    }
    setPushing(false)
  }

  async function disconnect() {
    setDisconnecting(false)
    setError(null)
    try {
      await api.disconnectRepository(course, subject)
      setRepository(connection?.repository ?? '')
      setPushed(null)
      setConnection(await api.repository(course, subject))
    } catch (e) {
      setError(sentence((e as Error).message))
    }
  }

  return (
    <section className="card repository-panel" aria-label={`Repository of ${subjectName}`}>
      <h3>Repository</h3>
      {connection === undefined && !error && <p className="note">Opening…</p>}

      {connection && !connection.connected && (
        <form className="key-form" aria-label="Connect to a repository" onSubmit={connect}>
          <p className="note">
            Push your notes, highlights, summaries, quizzes and flashcards of {subjectName} to a GitHub repository of
            yours, with a token that may write to it: a{' '}
            <a href={NEW_TOKEN} target="_blank" rel="noreferrer">
              fine-grained token
            </a>{' '}
            with read and write access to the repository's contents.
          </p>
          <label>
            Repository
            <input
              placeholder="owner/name"
              autoComplete="off"
              value={repository}
              onChange={(e) => setRepository(e.target.value)}
            />
          </label>
          <label>
            Token
            <input type="password" autoComplete="off" value={token} onChange={(e) => setToken(e.target.value)} />
          </label>
          <div className="actions">
            <button type="submit" disabled={connecting || !repository.trim() || !token.trim()}>
              {connecting ? 'Connecting…' : 'Connect'}
            </button>
          </div>
        </form>
      )}

      {connection?.connected && connection.repository && (
        <>
          <p>
            Connected to{' '}
            <a href={`https://github.com/${connection.repository}`} target="_blank" rel="noreferrer">
              {connection.repository}
            </a>
          </p>
          <p aria-label="Last pushed">
            {connection.pushed_at && connection.commit_url ? (
              <>
                Last pushed{' '}
                <a href={connection.commit_url} target="_blank" rel="noreferrer">
                  {when(connection.pushed_at)}
                </a>
              </>
            ) : (
              'Never pushed'
            )}
          </p>
          <div className="actions">
            <button type="button" disabled={pushing} onClick={push}>
              {pushing ? 'Pushing…' : 'Push'}
            </button>
            <button type="button" className="secondary danger" onClick={() => setDisconnecting(true)}>
              Disconnect
            </button>
          </div>
          {disconnecting && (
            <div className="card confirm" role="alertdialog" aria-label={`Disconnect ${subjectName}`}>
              <p>
                Disconnect {subjectName} from {connection.repository}? The app forgets its token;{' '}
                {connection.repository} is left as it is, with everything pushed to it.
              </p>
              <div className="actions">
                <button type="button" className="danger" onClick={disconnect}>
                  Yes, disconnect
                </button>
                <button type="button" className="secondary" onClick={() => setDisconnecting(false)}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {pushed && (
        <p role="status" className="note">
          {pushed.pushed && pushed.commit_url ? (
            <>
              The push {didWhat(pushed)}.{' '}
              <a href={pushed.commit_url} target="_blank" rel="noreferrer">
                See the commit
              </a>
            </>
          ) : (
            'Nothing new to push: the repository already has the subject as it is.'
          )}
        </p>
      )}

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
    </section>
  )
}
