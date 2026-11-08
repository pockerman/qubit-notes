import { useEffect, useRef, useState } from 'react'
import type { Tool } from '../api'

type Props = {
  // the tools attached to the material's subject
  tools: Tool[]
  // the tool that is open, if any
  open: string | null
  onOpen: (tool: string) => void
  className?: string
}

/** "Tools": the tools attached to a subject, to open one beside its material. None, no menu. */
export function ToolsMenu({ tools, open, onOpen, className }: Props) {
  const [expanded, setExpanded] = useState(false)
  const menu = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!expanded) return
    const away = (e: MouseEvent) => {
      if (menu.current && !menu.current.contains(e.target as Node)) setExpanded(false)
    }
    const escape = (e: KeyboardEvent) => e.key === 'Escape' && setExpanded(false)
    document.addEventListener('mousedown', away)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('mousedown', away)
      document.removeEventListener('keydown', escape)
    }
  }, [expanded])

  if (tools.length === 0) return null
  return (
    <div className="tools-menu" ref={menu}>
      <button
        type="button"
        className={className}
        aria-haspopup="menu"
        aria-expanded={expanded}
        aria-pressed={open !== null}
        onClick={() => setExpanded(!expanded)}
      >
        Tools ▾
      </button>
      {expanded && (
        <div role="menu" aria-label="Tools">
          {tools.map((tool) => (
            <button
              key={tool.id}
              type="button"
              role="menuitemcheckbox"
              aria-checked={open === tool.id}
              onClick={() => {
                setExpanded(false)
                onOpen(tool.id)
              }}
            >
              {tool.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
