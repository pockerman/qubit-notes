import { useEffect, useRef, useState, type ClipboardEvent, type DragEvent, type RefObject } from 'react'
import type { StudyApi } from './api'
import { slug } from './names'

const IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']

// an image added while editing, kept with the material once it's saved
export type ImageDraft = { file: File; url: string }

// where an image is kept with the material: images/<its name>, made unique among those already added
function imagePath(file: File, taken: Set<string>): string {
  const dot = file.name.lastIndexOf('.')
  const extension = dot > 0 ? file.name.slice(dot + 1).toLowerCase() : file.type.replace('image/', '')
  const stem = slug(dot > 0 ? file.name.slice(0, dot) : file.name) || 'image'
  let path = `images/${stem}.${extension}`
  for (let n = 2; taken.has(path); n++) path = `images/${stem}-${n}.${extension}`
  return path
}

export function captionOf(file: File): string {
  return file.name.replace(/\.[^.]+$/, '').replace(/[-_]+/g, ' ')
}

type Editing = {
  text: string
  setText: (text: string) => void
  textarea: RefObject<HTMLTextAreaElement | null>
  setError: (error: string | null) => void
}

/** The images added to Markdown as it's written or edited: by their path in the text, until the material is saved. */
export function useImageDrafts({ text, setText, textarea, setError }: Editing) {
  const [drafts, setDrafts] = useState<Map<string, ImageDraft>>(new Map())

  // the local copies of the images are let go when the editor is
  const urls = useRef<string[]>([])
  useEffect(() => () => urls.current.forEach(URL.revokeObjectURL), [])

  /** keeps the image and puts a reference to it, on a line of its own, where the cursor is */
  function insert(file: File, alt: string) {
    if (!IMAGE_TYPES.includes(file.type)) {
      setError(`${file.name} is not a PNG, JPEG, GIF or WebP image`)
      return
    }
    const path = imagePath(file, new Set(drafts.keys()))
    const url = URL.createObjectURL(file)
    urls.current.push(url)
    setDrafts(new Map(drafts).set(path, { file, url }))
    const reference = `![${alt.replace(/[[\]]/g, '')}](${path})`
    const at = textarea.current?.selectionStart ?? text.length
    const before = text.slice(0, at)
    const after = text.slice(textarea.current?.selectionEnd ?? at)
    const lead = before && !before.endsWith('\n') ? '\n' : ''
    setText(`${before}${lead}${reference}\n${after}`)
    setError(null)
  }

  function pasteOrDrop(files: FileList | undefined, event: ClipboardEvent | DragEvent) {
    const found = [...(files ?? [])].filter((file) => file.type.startsWith('image/'))
    if (!found.length) return
    event.preventDefault()
    found.forEach((file) => insert(file, captionOf(file)))
  }

  /** adds the images the saved text still refers to; what failed, if anything */
  async function keepWith(api: StudyApi, courseId: string, documentId: string, saved: string): Promise<string[]> {
    const failed: string[] = []
    for (const [path, { file }] of drafts) {
      // an image whose reference was deleted from the text isn't kept
      if (!saved.includes(`](${path})`)) continue
      try {
        await api.addImage(courseId, documentId, file, path)
      } catch (e) {
        failed.push(`${file.name}: ${(e as Error).message}`)
      }
    }
    return failed
  }

  return { drafts, insert, pasteOrDrop, keepWith }
}
