import { useState } from 'react'
import type { GoRun, StudyApi } from '../api'

export const STARTER = `package main

import "fmt"

func main() {
	fmt.Println("hello, world")
}
`

type Props = {
  api: StudyApi
  source: string
  onChange: (source: string) => void
  onClose: () => void
}

function ended(run: GoRun): string {
  if (run.timed_out) return 'It ran out of time, and was stopped.'
  if (run.truncated) return 'It printed too much, and was stopped.'
  return run.exit_code === 0 ? 'It ended normally.' : `It ended with exit code ${run.exit_code}.`
}

/** Writes and runs Go beside the text; what it printed is shown as text, whatever it says
 * (features/ui_go_editor.feature). */
export function GoEditor({ api, source, onChange, onClose }: Props) {
  const [run, setRun] = useState<GoRun | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function start() {
    if (running) return
    setRunning(true)
    setError(null)
    setRun(null)
    try {
      setRun(await api.runGo(source))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setRunning(false)
    }
  }

  return (
    <aside className="assistant go-editor" aria-label="Go editor">
      <header className="assistant-header">
        <h3>Go editor</h3>
        <span className="note">Ctrl+Enter runs it</span>
        <button type="button" className="link" aria-label="Close the Go editor" onClick={onClose}>
          ✕
        </button>
      </header>
      <textarea
        aria-label="Go program"
        spellCheck={false}
        rows={16}
        value={source}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault()
            void start()
          } else if (e.key === 'Tab' && !e.shiftKey) {
            // a tab, as Go is written; Shift+Tab still leaves the editor
            e.preventDefault()
            const { selectionStart: from, selectionEnd: to } = e.currentTarget
            const area = e.currentTarget
            onChange(`${source.slice(0, from)}\t${source.slice(to)}`)
            requestAnimationFrame(() => area.setSelectionRange(from + 1, from + 1))
          }
        }}
      />
      <div className="actions">
        <button type="button" disabled={running || !source.trim()} onClick={start}>
          {running ? 'Running…' : 'Run'}
        </button>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {run && (
        <>
          <pre className="go-output" aria-label="Output" tabIndex={0}>
            {run.output}
          </pre>
          <p role="status" className="note">
            {ended(run)}
          </p>
        </>
      )}
    </aside>
  )
}
