import { useState } from 'react'
import type { Original, StudyApi } from '../api'

/** The documents a subject's lessons were made from, each hidden until the student shows it: a PDF on the page, in
 * the browser's viewer; an EPUB, which a browser can't show, is downloaded (features/ui_lessons.feature). */
export function Originals({ api, courseId, originals }: { api: StudyApi; courseId: string; originals: Original[] }) {
  // the originals shown, by document id
  const [shown, setShown] = useState<Set<string>>(() => new Set())
  const [error, setError] = useState<string | null>(null)

  if (originals.length === 0) return null

  function toggle(id: string) {
    const next = new Set(shown)
    if (!next.delete(id)) next.add(id)
    setShown(next)
  }

  // any of its lessons downloads it
  async function download(original: Original) {
    try {
      const file = await api.download(courseId, original.lessons[0].document_id)
      const url = URL.createObjectURL(file.blob)
      const link = document.createElement('a')
      link.href = url
      link.download = file.filename ?? original.filename
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <section className="originals" aria-labelledby="originals-title">
      <h3 id="originals-title">Originals</h3>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <ul aria-label="Originals">
        {originals.map((original) => {
          const isShown = shown.has(original.document_id)
          const pdf = original.content_type === 'application/pdf'
          const count = original.lessons.length
          return (
            <li key={original.document_id} aria-label={original.filename}>
              <div className="original-header">
                <span className="filename">{original.filename}</span>
                <span className="note">made into {count === 1 ? '1 lesson' : `${count} lessons`}</span>
                {pdf && (
                  <button
                    type="button"
                    className="link"
                    aria-expanded={isShown}
                    aria-label={`${isShown ? 'Hide' : 'Show'} ${original.filename}`}
                    onClick={() => toggle(original.document_id)}
                  >
                    {isShown ? 'Hide' : 'Show'}
                  </button>
                )}
                <button
                  type="button"
                  className="link"
                  aria-label={`Download ${original.filename}`}
                  onClick={() => download(original)}
                >
                  Download
                </button>
              </div>
              {pdf && isShown && (
                <iframe
                  className="original-view"
                  title={original.filename}
                  src={api.fileUrl(courseId, original.lessons[0].document_id)}
                />
              )}
              {!pdf && <p className="note">A browser can't show an EPUB here: download it to read it.</p>}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
