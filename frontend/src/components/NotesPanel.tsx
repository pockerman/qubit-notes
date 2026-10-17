import { useState } from 'react'
import type { Note } from '../api'
import { formatMoment } from '../moments'

type Props = {
  notes: Note[]
  // clicking a note's anchor: shows its section, or plays the video from its moment
  onGoTo: (note: Note) => void
  onChange: (note: Note, text: string) => Promise<void>
  onDelete: (note: Note) => Promise<void>
}

function NoteItem({ note, onGoTo, onChange, onDelete }: { note: Note } & Omit<Props, 'notes'>) {
  const [editing, setEditing] = useState(false)
  const [text, setText] = useState(note.text)
  const anchor =
    note.at_seconds !== null ? formatMoment(note.at_seconds) : `${note.section_title || 'Start'} · “${note.passage}”`

  return (
    <li className="note-item" aria-label={`Note: ${note.text}`}>
      <button type="button" className="link anchor" onClick={() => onGoTo(note)}>
        {anchor}
      </button>
      {editing ? (
        <form
          onSubmit={async (e) => {
            e.preventDefault()
            await onChange(note, text)
            setEditing(false)
          }}
        >
          <label>
            Note
            <textarea value={text} onChange={(e) => setText(e.target.value)} rows={3} required />
          </label>
          <div className="actions">
            <button type="submit">Save</button>
            <button type="button" className="link" onClick={() => setEditing(false)}>
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <>
          <p>{note.text}</p>
          <div className="actions">
            <button type="button" className="link" onClick={() => setEditing(true)}>
              Edit
            </button>
            <button type="button" className="link" onClick={() => onDelete(note)}>
              Delete
            </button>
          </div>
        </>
      )}
    </li>
  )
}

export function NotesPanel({ notes, onGoTo, onChange, onDelete }: Props) {
  return (
    <aside className="notes" aria-label="My notes">
      <h3>My notes</h3>
      {notes.length === 0 ? (
        <p className="note">No notes yet.</p>
      ) : (
        <ul>
          {notes.map((note) => (
            <NoteItem key={note.id} note={note} onGoTo={onGoTo} onChange={onChange} onDelete={onDelete} />
          ))}
        </ul>
      )}
    </aside>
  )
}
