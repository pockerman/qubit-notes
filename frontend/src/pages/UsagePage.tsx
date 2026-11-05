import { useEffect, useState, type ReactNode } from 'react'
import type { Me, Spent, StudentUsage, StudyApi, Usage } from '../api'
import { PROVIDER } from '../providers'
import { href } from '../router'

const PURPOSES: Record<string, string> = {
  assistant: 'The assistant',
  summary: 'Summaries',
  quiz: 'Quizzes',
  flashcards: 'Flashcards',
  generating: 'Generated material',
}

const tokens = (spent: Spent) => (spent.input_tokens + spent.output_tokens).toLocaleString()

/** The tokens the AI has used for the student, and for an admin, for each student (features/ui_ai_usage.feature). */
export function UsagePage({ api }: { api: StudyApi }) {
  const [usage, setUsage] = useState<Usage | null>(null)
  const [me, setMe] = useState<Me | null>(null)
  const [students, setStudents] = useState<StudentUsage[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.usage().then(setUsage, (e: Error) => setError(e.message))
    api.me().then(setMe, () => setMe(null))
  }, [api])

  useEffect(() => {
    if (me?.admin) api.studentsUsage().then(setStudents, (e: Error) => setError(e.message))
  }, [api, me])

  return (
    <section className="settings" aria-labelledby="settings-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'courses' })}>
          ← My courses
        </a>
        <h2 id="settings-title">Settings</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {usage && (
        <section className="card" aria-labelledby="usage-title">
          <h3 id="usage-title">Usage</h3>
          <p>
            You have used <strong>{tokens(usage)}</strong> tokens in the last {usage.days} days.
          </p>
          {usage.purposes.length > 0 && (
            <SpentTable label="Tokens by what they were used on" heading="Used on">
              {usage.purposes.map((spent) => (
                <SpentRow key={spent.purpose} name={PURPOSES[spent.purpose] ?? spent.purpose} spent={spent} />
              ))}
            </SpentTable>
          )}
          {usage.models.length > 0 && (
            <SpentTable label="Tokens by model" heading="Model">
              {usage.models.map((spent) => (
                <SpentRow
                  key={`${spent.provider}/${spent.model}`}
                  name={`${PROVIDER[spent.provider] ?? spent.provider} · ${spent.model}`}
                  spent={spent}
                />
              ))}
            </SpentTable>
          )}
        </section>
      )}
      {students && (
        <section className="card" aria-labelledby="students-usage-title">
          <h3 id="students-usage-title">Students</h3>
          {students.length === 0 ? (
            <p className="note">No one has used the AI in this time.</p>
          ) : (
            <SpentTable label="Tokens by student" heading="Student">
              {students.map((spent) => (
                <SpentRow key={spent.student} name={spent.student} spent={spent} />
              ))}
            </SpentTable>
          )}
        </section>
      )}
    </section>
  )
}

function SpentTable({ label, heading, children }: { label: string; heading: string; children: ReactNode }) {
  return (
    <div className="table-scroll">
      <table className="usage-table" aria-label={label}>
        <thead>
          <tr>
            <th scope="col">{heading}</th>
            <th scope="col">Requests</th>
            <th scope="col">Input</th>
            <th scope="col">Output</th>
            <th scope="col">Tokens</th>
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  )
}

function SpentRow({ name, spent }: { name: string; spent: Spent }) {
  return (
    <tr>
      <th scope="row">{name}</th>
      <td className="tokens">{spent.requests.toLocaleString()}</td>
      <td className="tokens">{spent.input_tokens.toLocaleString()}</td>
      <td className="tokens">{spent.output_tokens.toLocaleString()}</td>
      <td className="tokens">{tokens(spent)}</td>
    </tr>
  )
}
