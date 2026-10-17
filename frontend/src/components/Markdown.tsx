import type { ReactNode } from 'react'

/** Inline **bold**, *italic* and `code`, as React elements: the text is never treated as HTML. */
function inline(text: string): ReactNode[] {
  const parts: ReactNode[] = []
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g
  let cursor = 0
  for (const match of text.matchAll(pattern)) {
    parts.push(text.slice(cursor, match.index))
    const token = match[0]
    if (token.startsWith('**')) parts.push(<strong key={match.index}>{token.slice(2, -2)}</strong>)
    else if (token.startsWith('`')) parts.push(<code key={match.index}>{token.slice(1, -1)}</code>)
    else parts.push(<em key={match.index}>{token.slice(1, -1)}</em>)
    cursor = (match.index ?? 0) + token.length
  }
  parts.push(text.slice(cursor))
  return parts
}

/** The Markdown the AI writes summaries in: headings, bullet and numbered lists, and paragraphs. */
export function Markdown({ text }: { text: string }) {
  const blocks: ReactNode[] = []
  let list: { ordered: boolean; items: string[] } | null = null
  let paragraph: string[] = []

  const flush = () => {
    if (paragraph.length) {
      blocks.push(<p key={blocks.length}>{inline(paragraph.join(' '))}</p>)
      paragraph = []
    }
    if (list) {
      const items = list.items.map((item, i) => <li key={i}>{inline(item)}</li>)
      blocks.push(list.ordered ? <ol key={blocks.length}>{items}</ol> : <ul key={blocks.length}>{items}</ul>)
      list = null
    }
  }

  for (const line of text.split('\n')) {
    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    const bullet = line.match(/^\s*[-*]\s+(.*)$/)
    const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/)
    if (heading) {
      flush()
      const level = Math.min(heading[1].length + 3, 6)
      const Tag = `h${level}` as 'h4' | 'h5' | 'h6'
      blocks.push(<Tag key={blocks.length}>{inline(heading[2])}</Tag>)
    } else if (bullet || numbered) {
      const ordered = Boolean(numbered)
      if (paragraph.length || (list && list.ordered !== ordered)) flush()
      list = list ?? { ordered, items: [] }
      list.items.push((bullet ?? numbered)![1])
    } else if (!line.trim()) {
      flush()
    } else {
      if (list) flush()
      paragraph.push(line.trim())
    }
  }
  flush()
  return <div className="markdown">{blocks}</div>
}
