import { useEffect, useRef, useState } from 'react'
import type { MaterialImages, StudyApi } from '../api'
import { IMAGE_ACCEPT } from '../images'

type Props = {
  api: StudyApi
  courseId: string
  documentId: string
  path: string
  alt: string
  missing: boolean
  // owners add a missing image; called with the material's images once it's added
  onAdd?: (images: MaterialImages) => void
}

/** An image kept with a material. It's fetched as the student, since a plain <img src> can't say who they are. */
export function MaterialImage({ api, courseId, documentId, path, alt, missing, onAdd }: Props) {
  const [url, setUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const picker = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (missing) return
    let objectUrl: string | null = null
    let cancelled = false
    api.image(courseId, documentId, path).then(
      (blob) => {
        if (cancelled) return
        objectUrl = URL.createObjectURL(blob)
        setUrl(objectUrl)
      },
      (e: Error) => !cancelled && setError(e.message),
    )
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [api, courseId, documentId, path, missing])

  async function add(file: File | undefined) {
    if (!file || !onAdd) return
    try {
      onAdd(await api.addImage(courseId, documentId, file, path))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  if (missing || error) {
    return (
      <span className="image-missing" role="group" aria-label={`Missing image ${path}`}>
        <span>
          {missing ? 'Missing image' : 'Image not shown'}: <code>{path}</code>
          {alt && ` (${alt})`}
        </span>
        {error && <span className="error"> {error}</span>}
        {missing && onAdd && (
          <>
            <button type="button" className="link" onClick={() => picker.current?.click()}>
              Add the missing image
            </button>
            <input
              ref={picker}
              type="file"
              accept={IMAGE_ACCEPT}
              hidden
              aria-label={`Image for ${path}`}
              onChange={(e) => add(e.target.files?.[0])}
            />
          </>
        )}
      </span>
    )
  }
  return url ? <img className="material-image" src={url} alt={alt} /> : <span className="note">Loading image…</span>
}
