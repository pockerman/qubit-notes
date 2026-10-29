import { useEffect, useState, type ReactNode } from 'react'
import { shownAs } from '../references'

// marks passages in the plain text of a block, e.g. those that have notes; the text is never treated as HTML
export type Highlighter = (text: string) => ReactNode

const plain: Highlighter = (text) => text

// shows an image the text refers to, e.g. one kept with the material; `src` is as written in the Markdown
export type ImageRenderer = (src: string, alt: string, key: number) => ReactNode

// shows a reference to another part of the course, e.g. [[subject/topic]]; `written` is as in the Markdown
export type ReferenceRenderer = (written: string, key: number) => ReactNode

/** A reference is shown as its label, or the name of what it refers to, until a ReferenceRenderer knows where to. */
const asText: ReferenceRenderer = (written, key) => <span key={key}>{shownAs(written)}</span>

/** Images on the web are shown as they are; others are only shown by an ImageRenderer that knows where they are. */
const webOnly: ImageRenderer = (src, alt, key) =>
  /^https:/i.test(src) ? (
    <img key={key} src={src} alt={alt} loading="lazy" referrerPolicy="no-referrer" />
  ) : (
    <span key={key} className="image-missing" role="img" aria-label={`${alt} (not shown)`}>
      {alt || src}
    </span>
  )

/** the path of an image as written, without the title or angle brackets Markdown allows, or a leading ./ */
function imageSource(target: string): string {
  return target
    .replace(/\s+"[^"]*"\s*$/, '')
    .trim()
    .replace(/^<(.*)>$/, '$1')
    .replace(/^\.\//, '')
}

/** Links to the web only, so a material can't link to a script. */
function safeHref(href: string): string | undefined {
  return /^(https?:|mailto:)/i.test(href) ? href : undefined
}

type Katex = typeof import('katex').default

let katex: Katex | undefined
let loading: Promise<Katex> | undefined

/** KaTeX and its stylesheet, fetched the first time a page has mathematics, so pages without any don't wait for it */
function loadKatex(): Promise<Katex> {
  loading ??= Promise.all([import('katex'), import('katex/dist/katex.min.css')]).then(
    ([module]) => (katex = module.default),
    (e) => {
      // tried again by the next mathematics shown, e.g. once back online
      loading = undefined
      throw e
    },
  )
  return loading
}

function useKatex(): Katex | undefined {
  const [loaded, setLoaded] = useState(katex)
  useEffect(() => {
    if (!loaded) loadKatex().then(setLoaded, () => {})
  }, [loaded])
  return loaded
}

/**
 * Mathematics in LaTeX, typeset by KaTeX: in the text, or on a line of its own. Until KaTeX is loaded it is shown as
 * written. LaTeX KaTeX can't typeset is shown as written, marked as such. KaTeX's HTML is its own, from the LaTeX,
 * which can't run scripts or link anywhere.
 */
function Maths({ tex, display = false }: { tex: string; display?: boolean }) {
  const katex = useKatex()
  if (!katex) return <span className={display ? 'math-loading math-display' : 'math-loading'}>{tex}</span>
  try {
    const html = katex.renderToString(tex, { displayMode: display, throwOnError: true, trust: false })
    // a span, as display mathematics may be in a paragraph too; the stylesheet puts it on a line of its own
    return <span className={display ? 'math math-display' : 'math'} dangerouslySetInnerHTML={{ __html: html }} />
  } catch (e) {
    return (
      <code className="math-error" title={`Could not typeset this: ${(e as Error).message}`}>
        {tex}
      </code>
    )
  }
}

// mathematics in the text: $$…$$ and \[…\] on a line of its own, \(…\), and $…$ as Pandoc reads it: no space just
// inside its dollars, and no digit just after, so "$5, or $10" is not mathematics
const MATHS = String.raw`\$\$[^$]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$(?=\S)(?:\\\$|[^$])*?[^\s\\]\$(?!\d)`

/** the LaTeX of mathematics in the text, without its delimiters, and whether it is on a line of its own */
function maths(token: string): { tex: string; display: boolean } {
  if (token.startsWith('$$')) return { tex: token.slice(2, -2).trim(), display: true }
  if (token.startsWith('\\[')) return { tex: token.slice(2, -2).trim(), display: true }
  if (token.startsWith('\\(')) return { tex: token.slice(2, -2).trim(), display: false }
  return { tex: token.slice(1, -1), display: false }
}

// a link written in HTML, <a href="https://…">label</a>: shown as a link like [label](https://…), never as HTML
const HTML_LINK = /<[aA]\s[^>]*?\bhref\s*=\s*(?:"[^"]*"|'[^']*')[^>]*>.*?<\/[aA]>/

/** the label and target of a link, written [label](href) or <a href="href">label</a> */
function link(token: string): { label: string; href: string } {
  if (token.startsWith('[')) {
    const [, label, href] = token.match(/^\[([^\]]+)\]\(([^)\s]+)\)$/)!
    return { label, href }
  }
  const [, double, single] = token.match(/\shref\s*=\s*(?:"([^"]*)"|'([^']*)')/i)!
  return { label: token.match(/>(.*)<\/a>$/i)![1], href: double ?? single }
}

/**
 * Inline **bold**, *italic*, `code`, [links](https://…) and <a href="https://…">links</a>, [[references]] and
 * $mathematics$, as React elements.
 */
function inline(text: string, mark: Highlighter, image: ImageRenderer, reference: ReferenceRenderer): ReactNode[] {
  const parts: ReactNode[] = []
  const pattern = new RegExp(
    String.raw`(\[\[[^[\]]+\]\]|!\[[^\]]*\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|` +
      // code in a run of backticks, closed by a run as long, e.g. `code` or ```code```
      '(?<!`)(?<ticks>`+)(?!`).+?(?<!`)\\k<ticks>(?!`)' +
      String.raw`|\[[^\]]+\]\([^)\s]+\)|${HTML_LINK.source}|${MATHS}|\\\$)`,
    'g',
  )
  let cursor = 0
  for (const match of text.matchAll(pattern)) {
    const at = match.index ?? 0
    parts.push(mark(text.slice(cursor, at)))
    const token = match[0]
    if (token === '\\$') parts.push(mark('$'))
    else if (/^(\$|\\[[(])/.test(token)) {
      const { tex, display } = maths(token)
      parts.push(<Maths key={at} tex={tex} display={display} />)
    } else if (token.startsWith('[[')) parts.push(reference(token, at))
    else if (token.startsWith('![')) {
      const [, alt, target] = token.match(/^!\[([^\]]*)\]\(([^)]+)\)$/)!
      parts.push(image(imageSource(target), alt, at))
    } else if (token.startsWith('**'))
      parts.push(<strong key={at}>{inline(token.slice(2, -2), mark, image, reference)}</strong>)
    else if (token.startsWith('`')) {
      const ticks = match.groups!.ticks.length
      // a space on both sides lets the code start or end with a backtick, as in `` `x` ``; it isn't the code's
      const code = token.slice(ticks, -ticks).replace(/^ (.*) $/, '$1')
      parts.push(<code key={at}>{code}</code>)
    }
    else if (token.startsWith('[') || token.startsWith('<')) {
      const { label, href } = link(token)
      parts.push(
        <a key={at} href={safeHref(href)} target="_blank" rel="noreferrer">
          {inline(label, mark, image, reference)}
        </a>,
      )
    } else parts.push(<em key={at}>{inline(token.slice(1, -1), mark, image, reference)}</em>)
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
  image?: ImageRenderer
  reference?: ReferenceRenderer
}

/** Markdown: headings, paragraphs, bullet and numbered lists, tables, code blocks, quotes, rules and mathematics. */
export function Markdown({ text, headingOffset = 3, mark = plain, image = webOnly, reference = asText }: Props) {
  const blocks: ReactNode[] = []
  let list: { ordered: boolean; items: string[] } | null = null
  let paragraph: string[] = []
  let quote: string[] = []

  const flush = () => {
    if (paragraph.length) {
      blocks.push(<p key={blocks.length}>{inline(paragraph.join(' '), mark, image, reference)}</p>)
      paragraph = []
    }
    if (list) {
      const items = list.items.map((item, i) => <li key={i}>{inline(item, mark, image, reference)}</li>)
      blocks.push(list.ordered ? <ol key={blocks.length}>{items}</ol> : <ul key={blocks.length}>{items}</ul>)
      list = null
    }
    if (quote.length) {
      blocks.push(<blockquote key={blocks.length}>{inline(quote.join(' '), mark, image, reference)}</blockquote>)
      quote = []
    }
  }

  const lines = text.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    // ```code``` on a line of its own is code in the text, as a ``` fence has no ` after it
    const fence = line.match(/^\s*(```(?!.*`)|~~~)/)
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
                  <th key={j}>{inline(cell, mark, image, reference)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, r) => (
                <tr key={r}>
                  {header.map((_, j) => (
                    <td key={j}>{inline(row[j] ?? '', mark, image, reference)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      )
      continue
    }

    const opening = line.trim().match(/^(\$\$|\\\[)/)
    if (opening) {
      // mathematics on lines of its own, up to the line that closes it: $$ … $$, or \[ … \]
      const close = opening[1] === '$$' ? '$$' : '\\]'
      const found: string[] = []
      let end = i
      for (let rest = line.trim().slice(2); end < lines.length; rest = lines[++end]?.trim() ?? '') {
        if (rest.endsWith(close)) {
          found.push(rest.slice(0, -close.length))
          break
        }
        found.push(rest)
      }
      // a block that isn't closed, or that has more after it on its line, is text
      if (end < lines.length && !found.some((part) => part.includes(close))) {
        flush()
        blocks.push(
          <div className="math-block" key={blocks.length}>
            <Maths tex={found.join('\n').trim()} display />
          </div>,
        )
        i = end
        continue
      }
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    const bullet = line.match(/^\s*[-*+]\s+(.*)$/)
    const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/)
    const quoted = line.match(/^\s*>\s?(.*)$/)
    if (heading) {
      flush()
      const level = Math.min(heading[1].length + headingOffset, 6)
      const Tag = `h${level}` as 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
      blocks.push(<Tag key={blocks.length}>{inline(heading[2], mark, image, reference)}</Tag>)
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
