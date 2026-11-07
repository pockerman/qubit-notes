import { useEffect, useState } from 'react'
import type { StudyApi, Tool } from '../api'

type Props = {
  api: StudyApi
  chosen: string[]
  onChange: (tools: string[]) => void
}

/** The tools that can be attached to a subject, to choose some of. */
export function ToolChoice({ api, chosen, onChange }: Props) {
  const [tools, setTools] = useState<Tool[]>([])

  useEffect(() => {
    api.tools().then(setTools, () => setTools([]))
  }, [api])

  if (tools.length === 0) return null
  return (
    <fieldset className="tool-choice">
      <legend>Tools</legend>
      {tools.map((tool) => (
        <label key={tool.id} className="choice">
          <input
            type="checkbox"
            checked={chosen.includes(tool.id)}
            onChange={(e) =>
              onChange(e.target.checked ? [...chosen, tool.id] : chosen.filter((t) => t !== tool.id))
            }
          />
          {tool.name}
        </label>
      ))}
    </fieldset>
  )
}
