import { useEffect, useState } from 'react'
import type { StudyApi, Tool } from '../api'

type Props = {
  api: StudyApi
  chosen: string[]
  onChange: (tools: string[]) => void
  // where the choice can be closed, e.g. on a subject's page
  onClose?: () => void
}

/** The tools that can be attached to a subject, to choose some of. */
export function ToolChoice({ api, chosen, onChange, onClose }: Props) {
  // undefined while they're asked for, null when they couldn't be
  const [tools, setTools] = useState<Tool[] | null | undefined>(undefined)

  useEffect(() => {
    api.tools().then(setTools, () => setTools(null))
  }, [api])

  return (
    <fieldset className="tool-choice closable">
      <legend>Tools</legend>
      {onClose && (
        <button type="button" className="icon close" aria-label="Close the tools" onClick={onClose}>
          ✕
        </button>
      )}
      <p className="note">Attach tools to the subject's notes. They are under "Tools" when you read or write them.</p>
      {tools === undefined && <p className="note">Finding the tools…</p>}
      {tools === null && (
        <p role="alert" className="error">
          The tools couldn't be found.
        </p>
      )}
      {tools?.map((tool) => (
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
