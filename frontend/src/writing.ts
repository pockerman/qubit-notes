import type { WritingReply } from './api'

/** A section of a Markdown text: its heading's title, and where its text (after the heading) starts and ends. */
export type TextSection = { title: string; start: number; end: number }

const HEADING = /^(#{1,6})\s+(.+?)\s*#*\s*$/

/** The text's sections, each up to the next heading of its level or higher; headings in code blocks don't count. */
export function sectionsOf(text: string): TextSection[] {
  const headings: { level: number; title: string; at: number; textStart: number }[] = []
  let offset = 0
  let fenced = false
  for (const line of text.split(/(?<=\n)/)) {
    const bare = line.replace(/\n$/, '')
    if (bare.trimStart().startsWith('```')) fenced = !fenced
    else if (!fenced) {
      const heading = HEADING.exec(bare)
      if (heading)
        headings.push({ level: heading[1].length, title: heading[2], at: offset, textStart: offset + line.length })
    }
    offset += line.length
  }
  return headings.map((heading, i) => {
    const next = headings.slice(i + 1).find((h) => h.level <= heading.level)
    return { title: heading.title, start: heading.textStart, end: next ? next.at : text.length }
  })
}

/** The reply as it goes into the material: its markers, [1], linking to their sources, and its references after it. */
export function withReferences(reply: WritingReply): string {
  const linked = reply.reply.replace(/\[(\d+)\](?!\()/g, (marker, n: string) => {
    const source = reply.sources[Number(n) - 1]
    return source ? `[[${n}]](${source.url})` : marker
  })
  if (reply.sources.length === 0) return linked.trim()
  const references = reply.sources.map((source, i) => `${i + 1}. [${source.title}](${source.url})`).join('\n')
  return `${linked.trim()}\n\n**References**\n\n${references}`
}

/** The text with the section's text, after its heading, replaced; the text as it is if it has no such section. */
export function replaceSection(text: string, title: string, replacement: string): string {
  const section = sectionsOf(text).find((s) => s.title === title)
  if (!section) return text
  const after = text.slice(section.end)
  return `${text.slice(0, section.start)}\n${replacement.trim()}\n${after ? `\n${after.replace(/^\n+/, '')}` : ''}`
}

/** The text with what is added after the rest of it. */
export function addAtEnd(text: string, added: string): string {
  return text.trim() ? `${text.trimEnd()}\n\n${added.trim()}\n` : `${added.trim()}\n`
}
