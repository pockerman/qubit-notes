import type { ReactNode } from 'react'

// marks passages in the plain text of a block, e.g. those that have notes; the text is never treated as HTML
export type Highlighter = (text: string) => ReactNode

const plain: Highlighter = (text) => text

/** Links to the web only, so a material can't link to a script. */
function safeHref(href: string): string | undefined {
  return /^(https?:|mailto:)/i.test(href) ? href : undefined
}

/** Inline **bold**, *italic*, `code` and [links](https://…), as React elements. */
function inline(text: string, mark: Highlighter): ReactNode[] {
  const parts: ReactNode[] = []
  const pattern = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)\s]+\))/g
  let cursor = 0
  for (const match of text.matchAll(pattern)) {
    const at = match.index ?? 0
    parts.push(mark(text.slice(cursor, at)))
    const token = match[0]
    if (token.startsWith('**')) parts.push(<strong key={at}>{inline(token.slice(2, -2), mark)}</strong>)
    else if (token.startsWith('`')) parts.push(<code key={at}>{token.slice(1, -1)}</code>)
    else if (token.startsWith('[')) {
      const [, label, href] = token.match(/^\[([^\]]+)\]\(([^)\s]+)\)$/)!
      parts.push(
        <a key={at} href={safeHref(href)} target="_blank" rel="noreferrer">
          {inline(label, mark)}
        </a>,
      )
    } else parts.push(<em key={at}>{inline(token.slice(1, -1), mark)}</em>)
    cursor = at + token.length
  }
  parts.push(mark(text.slice(cursor)))
  return parts
}

const TABLE_ROW = /^\s*\|.*\|\s*$/
const TABLE_RULE = /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$/

function cells(row: string): string[] {
  return row
    .trim()
    .replace(/^\||\|$/g, '')
    .split(/(?<!\\)\|/)
    .map((cell) => cell.trim().replace(/\\\|/g, '|'))
}

type Props = {
  text: string
  // how much to lower headings, so they sit below the page's own; # becomes h(1 + headingOffset)
  headingOffset?: number
  mark?: Highlighter
}

/** Markdown: headings, paragraphs, bullet and numbered lists, tables, code blocks, quotes and rules. */
export function Markdown({ text, headingOffset = 3, mark = plain }: Props) {
  const blocks: ReactNode[] = []
  let list: { ordered: boolean; items: string[] } | null = null
  let paragraph: string[] = []
  let quote: string[] = []

  const flush = () => {
    if (paragraph.length) {
      blocks.push(<p key={blocks.length}>{inline(paragraph.join(' '), mark)}</p>)
      paragraph = []
    }
    if (list) {
      const items = list.items.map((item, i) => <li key={i}>{inline(item, mark)}</li>)
      blocks.push(list.ordered ? <ol key={blocks.length}>{items}</ol> : <ul key={blocks.length}>{items}</ul>)
      list = null
    }
    if (quote.length) {
      blocks.push(<blockquote key={blocks.length}>{inline(quote.join(' '), mark)}</blockquote>)
      quote = []
    }
  }

  const lines = text.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const fence = line.match(/^\s*(```|~~~)/)
    if (fence) {
      flush()
      const code: string[] = []
      for (i++; i < lines.length && !lines[i].trim().startsWith(fence[1]); i++) code.push(lines[i])
      blocks.push(
        <pre key={blocks.length}>
          <code>{code.join('\n')}</code>
        </pre>,
      )
      continue
    }
    if (TABLE_ROW.test(line) && i + 1 < lines.length && TABLE_RULE.test(lines[i + 1])) {
      flush()
      const header = cells(line)
      const rows: string[][] = []
      for (i += 2; i < lines.length && TABLE_ROW.test(lines[i]); i++) rows.push(cells(lines[i]))
      i--
      blocks.push(
        <div className="table-scroll" key={blocks.length}>
          <table>
            <thead>
              <tr>
                {header.map((cell, j) => (
                  <th key={j}>{inline(cell, mark)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, r) => (
                <tr key={r}>
                  {header.map((_, j) => (
                    <td key={j}>{inline(row[j] ?? '', mark)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      )
      continue
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    const bullet = line.match(/^\s*[-*+]\s+(.*)$/)
    const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/)
    const quoted = line.match(/^\s*>\s?(.*)$/)
    if (heading) {
      flush()
      const level = Math.min(heading[1].length + headingOffset, 6)
      const Tag = `h${level}` as 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
      blocks.push(<Tag key={blocks.length}>{inline(heading[2], mark)}</Tag>)
    } else if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) {
      flush()
      blocks.push(<hr key={blocks.length} />)
    } else if (bullet || numbered) {
      const ordered = Boolean(numbered)
      if (paragraph.length || quote.length || (list && list.ordered !== ordered)) flush()
      list = list ?? { ordered, items: [] }
      list.items.push((bullet ?? numbered)![1])
    } else if (quoted) {
      if (paragraph.length || list) flush()
      quote.push(quoted[1])
    } else if (!line.trim()) {
      flush()
    } else if (list && /^\s{2,}\S/.test(line)) {
      // a list item continued on the next line
      list.items[list.items.length - 1] += ` ${line.trim()}`
    } else {
      if (list || quote.length) flush()
      paragraph.push(line.trim())
    }
  }
  flush()
  return <div className="markdown">{blocks}</div>
}
