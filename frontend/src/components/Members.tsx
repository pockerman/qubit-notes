import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Course, Member, Role, StudyApi } from '../api'

type Props = {
  api: StudyApi
  course: Course
  // a collection of papers, shared as a course is, but known by its id
  collection?: boolean
}

/** Who a course, or a collection of papers, is shared with; any member sees them, only owners share it. */
export function Members({ api, course, collection = false }: Props) {
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

  const calls = collection
    ? {
        share: (student: string, role: Role) => api.shareCollection(course.id, student, role),
        unshare: (student: string) => api.unshareCollection(course.id, student),
      }
    : {
        share: (student: string, role: Role) => api.share(course.name, student, role),
        unshare: (student: string) => api.unshare(course.name, student),
      }

  useEffect(() => {
    run(collection ? () => api.collectionMembers(course.id) : () => api.members(course.name))
  }, [api, course.id, course.name, collection, run])

  function share(event: FormEvent) {
    event.preventDefault()
    if (!student.trim()) return
    run(() => calls.share(student.trim(), role)).then(() => setStudent(''))
  }

  return (
    <section className="members card">
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
                onClick={() => run(() => calls.unshare(member.student))}
              >
                Remove
              </button>
            )}
          </li>
        ))}
      </ul>

      {isOwner && (
        <form className="share" onSubmit={share} aria-label={collection ? 'Share this collection' : 'Share this course'}>
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
