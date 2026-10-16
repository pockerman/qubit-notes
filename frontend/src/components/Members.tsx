import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Course, Member, Role, StudyApi } from '../api'

export function Members({ api, course }: { api: StudyApi; course: Course }) {
  const [members, setMembers] = useState<Member[]>([])
  const [student, setStudent] = useState('')
  const [role, setRole] = useState<Role>('reader')
  const [error, setError] = useState<string | null>(null)
  const isOwner = course.role === 'owner'

  const run = useCallback(
    (call: () => Promise<Member[]>) =>
      call().then(
        (updated) => {
          setMembers(updated)
          setError(null)
        },
        (e: Error) => setError(e.message),
      ),
    [],
  )

  useEffect(() => {
    run(() => api.members(course.name))
  }, [api, course.name, run])

  function share(event: FormEvent) {
    event.preventDefault()
    if (!student.trim()) return
    run(() => api.share(course.name, student.trim(), role)).then(() => setStudent(''))
  }

  return (
    <section className="members" aria-labelledby="members-title">
      <h3 id="members-title">Members</h3>
      <ul aria-label="Members">
        {members.map((member) => (
          <li key={member.student}>
            <span>{member.student}</span>
            <span className="badge">{member.role}</span>
            {isOwner && member.student !== api.student && (
              <button
                type="button"
                className="link"
                aria-label={`Stop sharing with ${member.student}`}
                onClick={() => run(() => api.unshare(course.name, member.student))}
              >
                Remove
              </button>
            )}
          </li>
        ))}
      </ul>

      {isOwner && (
        <form className="share" onSubmit={share} aria-label="Share this course">
          <label>
            Classmate
            <input value={student} onChange={(e) => setStudent(e.target.value)} />
          </label>
          <label>
            Role
            <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
              <option value="reader">reader</option>
              <option value="owner">owner</option>
            </select>
          </label>
          <button type="submit">Share</button>
        </form>
      )}

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
    </section>
  )
}
