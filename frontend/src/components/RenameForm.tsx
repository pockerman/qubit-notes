import { useState, type FormEvent } from 'react'

/** Another name for a course, subject or topic; its id, in its links, stays. */
export function RenameForm({
  name,
  label = 'Name',
  onRename,
  onCancel,
}: {
  name: string
  // what the field is called, e.g. Title for a course
  label?: string
  onRename: (name: string) => Promise<void>
  onCancel: () => void
}) {
  const [value, setValue] = useState(name)
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    try {
      await onRename(value)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form className="card rename" aria-label={`Rename ${name}`} onSubmit={submit}>
      <label>
        {label}
        <input value={value} onChange={(e) => setValue(e.target.value)} required autoFocus />
      </label>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <div className="actions">
        <button type="submit" disabled={!value.trim()}>
          Rename
        </button>
        <button type="button" className="link" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}
