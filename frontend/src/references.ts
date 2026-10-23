/**
 * References from a Markdown material to another part of its course, as the backend reads them
 * (domain/reference_text.py): [[subject/topic]], [[subject/topic/material]] or [[subject/topic/material#section]],
 * with an optional label after a "|".
 */

const WRITTEN = /^\[\[([^[\]|#]*)(?:#([^[\]|]*))?(?:\|([^[\]]*))?\]\]$/

/** what a reference is shown as: its label, else the name of what it refers to */
export function shownAs(written: string): string {
  const match = written.match(WRITTEN)
  if (!match) return written
  const [, path, section, label] = match
  const parts = path.split('/').map((part) => part.trim())
  return label?.trim() || section?.trim() || (parts.every(Boolean) ? parts[parts.length - 1] : '') || written
}

/** the reference to a topic, or to one of its materials, or to a section of that */
export function referenceTo(subject: string, topic: string, material?: string, section?: string): string {
  const path = [subject, topic, ...(material ? [material] : [])].join('/')
  return `[[${path}${material && section ? `#${section}` : ''}]]`
}
