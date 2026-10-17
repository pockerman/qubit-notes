import { useEffect, useState } from 'react'
import type { OpenedMaterial, SectionText, StudyApi } from '../api'

type Props = {
  api: StudyApi
  courseId: string
  documentId: string
  onClose: () => void
}

function sectionLabel(title: string, filename: string): string {
  return title || filename
}

export function Reader({ api, courseId, documentId, onClose }: Props) {
  const [material, setMaterial] = useState<OpenedMaterial | null>(null)
  const [position, setPosition] = useState<number | null>(null)
  const [parts, setParts] = useState<SectionText[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.openMaterial(courseId, documentId).then(
      (opened) => {
        setMaterial(opened)
        setPosition(opened.sections[0]?.position ?? null)
      },
      (e: Error) => setError(e.message),
    )
  }, [api, courseId, documentId])

  useEffect(() => {
    if (position === null) return
    api.readSection(courseId, documentId, position).then(setParts, (e: Error) => setError(e.message))
  }, [api, courseId, documentId, position])

  async function download() {
    if (!material) return
    try {
      const url = URL.createObjectURL(await api.download(courseId, documentId))
      const link = document.createElement('a')
      link.href = url
      link.download = material.filename
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <section className="reader" aria-labelledby="reader-title">
      <header className="reader-header">
        <button type="button" className="link" onClick={onClose}>
          ← Back
        </button>
        <h2 id="reader-title">{material?.filename ?? 'Opening…'}</h2>
        {material && (
          <>
            <span className="note">
              {material.subject} › {material.topic}
            </span>
            <button type="button" onClick={download}>
              Download
            </button>
          </>
        )}
      </header>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {material && (
        <div className="reader-body">
          <nav aria-label="Sections" className="outline">
            <ol>
              {material.sections.map((section) => (
                <li key={section.position} style={{ paddingLeft: `${(section.level - 1) * 0.9}rem` }}>
                  <button
                    type="button"
                    className={section.position === position ? 'section-link selected' : 'section-link'}
                    aria-current={section.position === position ? 'true' : undefined}
                    onClick={() => setPosition(section.position)}
                  >
                    {sectionLabel(section.title, material.filename)}
                  </button>
                </li>
              ))}
            </ol>
          </nav>

          <article className="section-text" aria-label="Section text">
            {parts.map(({ section, content }, i) => {
              const Heading = i === 0 ? 'h3' : 'h4'
              return (
                <section key={section.position}>
                  <Heading>{sectionLabel(section.title, material.filename)}</Heading>
                  {content
                    .split(/\n\s*\n/)
                    .filter((paragraph) => paragraph.trim())
                    .map((paragraph, j) => (
                      <p key={j}>{paragraph}</p>
                    ))}
                </section>
              )
            })}
          </article>
        </div>
      )}
    </section>
  )
}
