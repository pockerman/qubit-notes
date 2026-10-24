import { useEffect, useRef, useState } from 'react'
import type { Material } from '../api'
import { STATUS_LABEL } from '../status'

type Props = {
  // all the materials of the topic, those that can't be chosen too
  materials: Material[]
  // the document ids chosen
  chosen: string[]
  onChange: (chosen: string[]) => void
  disabled?: boolean
}

// only ready text can be generated from
function canGenerateFrom(material: Material): boolean {
  return material.kind === 'text' && material.status === 'completed'
}

/** A drop-down menu of a topic's materials to tick, as many as wanted, or All of those that can be ticked. */
export function MaterialsMenu({ materials, chosen, onChange, disabled }: Props) {
  const [open, setOpen] = useState(false)
  const menu = useRef<HTMLDivElement>(null)
  const usable = materials.filter(canGenerateFrom)
  const all = usable.length > 0 && usable.every((m) => chosen.includes(m.document_id))

  // closes on a click outside it, or Escape
  useEffect(() => {
    if (!open) return
    const outside = (event: MouseEvent) => {
      if (!menu.current?.contains(event.target as Node)) setOpen(false)
    }
    const escape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', outside)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('mousedown', outside)
      document.removeEventListener('keydown', escape)
    }
  }, [open])

  function tick(material: Material, on: boolean) {
    onChange(on ? [...chosen, material.document_id] : chosen.filter((id) => id !== material.document_id))
  }

  let summary = 'Choose materials'
  if (all && usable.length > 1) summary = `All materials (${usable.length})`
  else if (chosen.length === 1) summary = materials.find((m) => m.document_id === chosen[0])?.filename ?? summary
  else if (chosen.length > 1) summary = `${chosen.length} materials`

  return (
    <div className="materials-menu" ref={menu}>
      <span id="materials-menu-label">Materials</span>
      <button
        type="button"
        aria-haspopup="true"
        aria-expanded={open}
        aria-labelledby="materials-menu-label materials-menu-summary"
        disabled={disabled}
        onClick={() => setOpen(!open)}
      >
        <span id="materials-menu-summary">{summary}</span> ▾
      </button>
      {open && (
        <ul className="menu" aria-label="Materials to generate from">
          <li>
            <label>
              <input
                type="checkbox"
                aria-label="Tick All"
                disabled={usable.length === 0}
                checked={all}
                onChange={(e) => onChange(e.target.checked ? usable.map((m) => m.document_id) : [])}
              />{' '}
              <span className="filename">All</span>
            </label>
          </li>
          {materials.map((material) => (
            <li key={material.document_id}>
              <label>
                <input
                  type="checkbox"
                  aria-label={`Tick ${material.filename}`}
                  disabled={!canGenerateFrom(material)}
                  checked={chosen.includes(material.document_id)}
                  onChange={(e) => tick(material, e.target.checked)}
                />{' '}
                <span className="filename">{material.filename}</span>
              </label>
              {!canGenerateFrom(material) && (
                <span className="note">
                  {material.kind === 'video' ? 'a video, with no text' : STATUS_LABEL[material.status]}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
