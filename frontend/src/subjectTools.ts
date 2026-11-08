import { useEffect, useState } from 'react'
import type { StudyApi } from './api'

/** The tools attached to a subject of a course (features/subject_tools.feature); none until they're known. */
export function useSubjectTools(api: StudyApi, courseId: string, subject: string | undefined): string[] {
  const [tools, setTools] = useState<string[]>([])

  useEffect(() => {
    if (!subject) return
    let current = true
    api
      .courses()
      .then((courses) => {
        const course = courses.find((c) => c.id === courseId)
        return course ? api.subjects(course.name) : []
      })
      .then(
        (subjects) => current && setTools(subjects.find((s) => s.subject === subject)?.tools ?? []),
        () => current && setTools([]),
      )
    return () => {
      current = false
    }
  }, [api, courseId, subject])

  return subject ? tools : []
}
