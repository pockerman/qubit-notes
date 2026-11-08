import { useState } from 'react'
import type { ProgramRun, StudyApi } from '../api'
import type { Language } from '../programs'

type Props = {
  api: StudyApi
  language: Language
  source: string
  onChange: (source: string) => void
  onClose: () => void
}

function ended(run: ProgramRun): string {
  if (run.timed_out) return 'It ran out of time, and was stopped.'
  if (run.truncated) return 'It printed too much, and was stopped.'
  // killed: in the sandbox, by its limit on memory
  if (run.exit_code === 137) return 'It ran out of memory, and was stopped (exit code 137).'
  return run.exit_code === 0 ? 'It ended normally.' : `It ended with exit code ${run.exit_code}.`
}

/** Writes and runs a program, in Go or Python, beside the text; what it printed is shown as text, whatever it says
 * (features/ui_go_editor.feature, features/ui_python_editor.feature). */
export function ProgramEditor({ api, language, source, onChange, onClose }: Props) {
  const [run, setRun] = useState<ProgramRun | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function start() {
    if (running) return
    setRunning(true)
    setError(null)
    setRun(null)
    try {
      setRun(await api.runProgram(language.id, source))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setRunning(false)
    }
  }

  return (
    <aside className="assistant program-editor" aria-label={`${language.name} editor`}>
      <header className="assistant-header">
        <h3>{language.name} editor</h3>
        <span className="note">Ctrl+Enter runs it</span>
        <button type="button" className="link" aria-label={`Close the ${language.name} editor`} onClick={onClose}>
          ✕
        </button>
      </header>
      <textarea
        aria-label={`${language.name} program`}
        spellCheck={false}
        rows={16}
        value={source}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault()
            void start()
          } else if (e.key === 'Tab' && !e.shiftKey) {
            // an indent, as the language is written; Shift+Tab still leaves the editor
            e.preventDefault()
            const { selectionStart: from, selectionEnd: to } = e.currentTarget
            const area = e.currentTarget
            const indent = language.indent
            onChange(`${source.slice(0, from)}${indent}${source.slice(to)}`)
            requestAnimationFrame(() => area.setSelectionRange(from + indent.length, from + indent.length))
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
          <pre className="program-output" aria-label="Output" tabIndex={0}>
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
