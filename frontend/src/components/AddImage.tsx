import { useState } from 'react'
import { captionOf } from '../imageDrafts'
import { IMAGE_ACCEPT } from '../images'

type Props = {
  onInsert: (file: File, alt: string) => void
}

/** Picks an image and its caption to insert into the Markdown being written. */
export function AddImage({ onInsert }: Props) {
  const [adding, setAdding] = useState(false)
  const [caption, setCaption] = useState('')
  const [picked, setPicked] = useState<File | null>(null)

  if (!adding) {
    return (
      <p className="note">
        <button type="button" className="link" onClick={() => setAdding(true)}>
          Add image
        </button>{' '}
        or paste or drop one into the text. PNG, JPEG, GIF or WebP, up to 10 MB.
      </p>
    )
  }
  return (
    <div className="add-image" role="group" aria-label="Add an image">
      <label>
        Image
        <input type="file" accept={IMAGE_ACCEPT} onChange={(e) => setPicked(e.target.files?.[0] ?? null)} />
      </label>
      <label>
        Caption
        <input value={caption} onChange={(e) => setCaption(e.target.value)} placeholder="A mesh of triangles" />
      </label>
      <div className="actions">
        <button
          type="button"
          disabled={!picked}
          onClick={() => {
            if (!picked) return
            onInsert(picked, caption.trim() || captionOf(picked))
            setAdding(false)
            setPicked(null)
            setCaption('')
          }}
        >
          Insert
        </button>
        <button type="button" className="link" onClick={() => setAdding(false)}>
          Cancel
        </button>
      </div>
    </div>
  )
}
