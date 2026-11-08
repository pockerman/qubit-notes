import { useEffect, useState } from 'react'
import type { StudyApi, Tool } from './api'

/** The tools attached to a subject of a course (features/subject_tools.feature); none until they're known. */
export function useSubjectTools(api: StudyApi, courseId: string, subject: string | undefined): Tool[] {
  const [tools, setTools] = useState<Tool[]>([])

  useEffect(() => {
    if (!subject) return
    let current = true
    const attached = api
      .courses()
      .then((courses) => {
        const course = courses.find((c) => c.id === courseId)
        return course ? api.subjects(course.name) : []
      })
      .then((subjects) => subjects.find((s) => s.subject === subject)?.tools ?? [])
    Promise.all([attached, api.tools()]).then(
      ([ids, all]) => current && setTools(all.filter((tool) => ids.includes(tool.id))),
      () => current && setTools([]),
    )
    return () => {
      current = false
    }
  }, [api, courseId, subject])

  return subject ? tools : []
}
