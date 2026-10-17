import { useEffect, useState } from 'react'

/**
 * The page shown, from the address's hash, so the browser's back button and a refresh keep the student where
 * they were:
 *   #/                                     my courses
 *   #/courses/<id>                         a course
 *   #/courses/<id>/add?subject=…&topic=…   adding material to it
 *   #/courses/<id>/materials/<document>    reading a material
 *   #/courses/<id>/topics/<subject>/<topic> studying a topic
 */
export type Route =
  | { page: 'courses' }
  | { page: 'course'; courseId: string }
  | { page: 'add'; courseId: string; subject: string; topic: string }
  | { page: 'material'; courseId: string; documentId: string }
  | { page: 'topic'; courseId: string; subject: string; topic: string }

export function parse(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?')
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent)
  const params = new URLSearchParams(query)
  if (parts[0] !== 'courses' || !parts[1]) return { page: 'courses' }
  const courseId = parts[1]
  if (parts[2] === 'add') {
    return { page: 'add', courseId, subject: params.get('subject') ?? '', topic: params.get('topic') ?? '' }
  }
  if (parts[2] === 'materials' && parts[3]) return { page: 'material', courseId, documentId: parts[3] }
  if (parts[2] === 'topics' && parts[3] && parts[4]) {
    return { page: 'topic', courseId, subject: parts[3], topic: parts[4] }
  }
  return { page: 'course', courseId }
}

export function href(route: Route): string {
  const course = (id: string) => `#/courses/${encodeURIComponent(id)}`
  switch (route.page) {
    case 'courses':
      return '#/'
    case 'course':
      return course(route.courseId)
    case 'add': {
      const query = new URLSearchParams({ subject: route.subject, topic: route.topic })
      return `${course(route.courseId)}/add?${query}`
    }
    case 'material':
      return `${course(route.courseId)}/materials/${encodeURIComponent(route.documentId)}`
    case 'topic':
      return `${course(route.courseId)}/topics/${encodeURIComponent(route.subject)}/${encodeURIComponent(route.topic)}`
  }
}

export function navigate(route: Route): void {
  window.location.hash = href(route)
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parse(window.location.hash))
  useEffect(() => {
    const update = () => setRoute(parse(window.location.hash))
    window.addEventListener('hashchange', update)
    return () => window.removeEventListener('hashchange', update)
  }, [])
  return route
}
