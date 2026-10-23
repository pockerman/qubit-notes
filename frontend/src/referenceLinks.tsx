import { useEffect, useState, type RefObject } from 'react'
import type { Reference, StudyApi } from './api'
import type { ReferenceRenderer } from './components/Markdown'
import { shownAs } from './references'
import { href } from './router'

/** where following a reference leads: the course at the topic, the material, or the material at the section */
function target(courseId: string, reference: Reference): string | null {
  const { refers_to, subject, topic, document_id, position } = reference
  if (refers_to === 'topic' && subject && topic) return href({ page: 'course', courseId, subject, topic })
  if (refers_to === 'material' && document_id) return href({ page: 'material', courseId, documentId: document_id })
  if (refers_to === 'section' && document_id && position) {
    return href({ page: 'material', courseId, documentId: document_id, section: position })
  }
  return null
}

/** Shows the references of a text as links to what they refer to; a broken one struck through, not as a link. */
export function referenceLinks(courseId: string, references: Reference[] | null): ReferenceRenderer {
  const byWritten = new Map((references ?? []).map((reference) => [reference.written, reference]))
  return (written, key) => {
    const reference = byWritten.get(written)
    if (!reference) return <span key={key}>{shownAs(written)}</span>
    const to = target(courseId, reference)
    if (!to) {
      return (
        <s key={key} className="reference-broken" title={`Broken reference: ${written} is not in the course`}>
          {reference.shown_as}
        </s>
      )
    }
    return (
      <a key={key} className="reference" href={to}>
        {reference.shown_as}
      </a>
    )
  }
}

/** The references of text being written, resolved again whenever it changes. */
export function useReferencesIn(api: StudyApi, courseId: string, text: string, active: boolean): Reference[] | null {
  const [references, setReferences] = useState<Reference[] | null>(null)
  useEffect(() => {
    if (!active || !text.includes('[[')) {
      setReferences([])
      return
    }
    let current = true
    api.referencesIn(courseId, text).then(
      (found) => current && setReferences(found),
      () => current && setReferences([]),
    )
    return () => {
      current = false
    }
  }, [api, courseId, text, active])
  return references
}

/** puts `inserted` where the cursor is in the textarea, after a space if it would run into a word */
export function insertAtCursor(
  text: string,
  setText: (text: string) => void,
  textarea: RefObject<HTMLTextAreaElement | null>,
  inserted: string,
) {
  const at = textarea.current?.selectionStart ?? text.length
  const before = text.slice(0, at)
  const after = text.slice(textarea.current?.selectionEnd ?? at)
  const lead = before && !/\s$/.test(before) ? ' ' : ''
  setText(`${before}${lead}${inserted}${after}`)
}
