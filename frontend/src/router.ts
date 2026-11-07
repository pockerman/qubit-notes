import { useEffect, useState } from 'react'

/**
 * The page shown, from the address's hash, so the browser's back button and a refresh keep the student where
 * they were:
 *   #/                                     my courses
 *   #/reviews                              the flashcards due for review, by course
 *   #/reviews/courses/<id>                 a course's, by subject and section
 *   #/reviews/courses/<id>/subjects/<subject>   reviewing a subject's
 *   #/reviews/courses/<id>/materials/<document>?section=<position>  reviewing a section's
 *   #/settings                             the app's settings: the AI's model
 *   #/settings/account                     the student's account: their email and password
 *   #/settings/usage                       the tokens the AI has used
 *   #/courses/<id>                         a course
 *   #/courses/<id>/subjects/<subject>      a subject: its topics
 *   #/courses/<id>/add?subject=…&topic=…   adding material to it
 *   #/courses/<id>/write?subject=…&topic=… writing material in a topic
 *   #/courses/<id>/generate?subject=…&topic=…  the AI writing material from a topic's
 *   #/courses/<id>/members                 who it is shared with
 *   #/courses/<id>/materials/<document>    reading a material
 *   #/courses/<id>/materials/<document>?section=<position>  reading it at a section
 *   #/courses/<id>/topics/<subject>/<topic> a topic: its material, and the assistant on all of it
 *   #/papers                               my collections of papers
 *   #/papers/<id>                          a collection: its papers, and the assistant on all of them
 *   #/papers/<id>/members                  who it is shared with
 *   #/papers/<id>/read/<document>          reading a paper
 *   #/papers/<id>/read/<document>?section=<position>  reading it at a section
 */
// the settings' views, under Settings in the app's menu
export type SettingsView = 'ai-model' | 'account' | 'usage'

// where in the reviews the student is: a course, to choose from, or a subject or a section of it, being reviewed
export type ReviewScope = { courseId: string; subject?: string; documentId?: string; section?: number }

export type Route =
  | { page: 'courses' }
  | { page: 'reviews'; scope?: ReviewScope }
  | { page: 'settings'; view: SettingsView }
  | { page: 'course'; courseId: string }
  | { page: 'subject'; courseId: string; subject: string }
  | { page: 'add'; courseId: string; subject: string; topic: string }
  | { page: 'members'; courseId: string }
  | { page: 'write'; courseId: string; subject: string; topic: string }
  | { page: 'generate'; courseId: string; subject: string; topic: string }
  | { page: 'material'; courseId: string; documentId: string; section?: number }
  | { page: 'topic'; courseId: string; subject: string; topic: string }
  | { page: 'papers' }
  | { page: 'collection'; collectionId: string }
  | { page: 'collection-members'; collectionId: string }
  | { page: 'paper'; collectionId: string; documentId: string; section?: number }

export function parse(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?')
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent)
  const params = new URLSearchParams(query)
  if (parts[0] === 'reviews') {
    if (parts[1] !== 'courses' || !parts[2]) return { page: 'reviews' }
    const courseId = parts[2]
    if (parts[3] === 'subjects' && parts[4]) return { page: 'reviews', scope: { courseId, subject: parts[4] } }
    const section = Number(params.get('section'))
    if (parts[3] === 'materials' && parts[4] && section > 0) {
      return { page: 'reviews', scope: { courseId, documentId: parts[4], section } }
    }
    return { page: 'reviews', scope: { courseId } }
  }
  if (parts[0] === 'settings') {
    return { page: 'settings', view: parts[1] === 'account' || parts[1] === 'usage' ? parts[1] : 'ai-model' }
  }
  if (parts[0] === 'papers') {
    const collectionId = parts[1]
    if (!collectionId) return { page: 'papers' }
    if (parts[2] === 'members') return { page: 'collection-members', collectionId }
    if (parts[2] === 'read' && parts[3]) {
      const section = Number(params.get('section'))
      return { page: 'paper', collectionId, documentId: parts[3], ...(section > 0 ? { section } : {}) }
    }
    return { page: 'collection', collectionId }
  }
  if (parts[0] !== 'courses' || !parts[1]) return { page: 'courses' }
  const courseId = parts[1]
  if (parts[2] === 'add') {
    return { page: 'add', courseId, subject: params.get('subject') ?? '', topic: params.get('topic') ?? '' }
  }
  if (parts[2] === 'members') return { page: 'members', courseId }
  if (parts[2] === 'generate') {
    return { page: 'generate', courseId, subject: params.get('subject') ?? '', topic: params.get('topic') ?? '' }
  }
  if (parts[2] === 'write') {
    return { page: 'write', courseId, subject: params.get('subject') ?? '', topic: params.get('topic') ?? '' }
  }
  if (parts[2] === 'materials' && parts[3]) {
    const section = Number(params.get('section'))
    return { page: 'material', courseId, documentId: parts[3], ...(section > 0 ? { section } : {}) }
  }
  if (parts[2] === 'subjects' && parts[3]) return { page: 'subject', courseId, subject: parts[3] }
  if (parts[2] === 'topics' && parts[3] && parts[4]) {
    return { page: 'topic', courseId, subject: parts[3], topic: parts[4] }
  }
  return { page: 'course', courseId }
}

export function href(route: Route): string {
  const course = (id: string) => `#/courses/${encodeURIComponent(id)}`
  const collection = (id: string) => `#/papers/${encodeURIComponent(id)}`
  switch (route.page) {
    case 'courses':
      return '#/'
    case 'reviews': {
      const { scope } = route
      if (!scope) return '#/reviews'
      const courseReviews = `#/reviews/courses/${encodeURIComponent(scope.courseId)}`
      if (scope.subject) return `${courseReviews}/subjects/${encodeURIComponent(scope.subject)}`
      if (!scope.documentId) return courseReviews
      return `${courseReviews}/materials/${encodeURIComponent(scope.documentId)}?section=${scope.section}`
    }
    case 'settings':
      return route.view === 'ai-model' ? '#/settings' : `#/settings/${route.view}`
    case 'course':
      return course(route.courseId)
    case 'subject':
      return `${course(route.courseId)}/subjects/${encodeURIComponent(route.subject)}`
    case 'add': {
      const query = new URLSearchParams({ subject: route.subject, topic: route.topic })
      return `${course(route.courseId)}/add?${query}`
    }
    case 'members':
      return `${course(route.courseId)}/members`
    case 'generate': {
      const query = new URLSearchParams({ subject: route.subject, topic: route.topic })
      return `${course(route.courseId)}/generate?${query}`
    }
    case 'write': {
      const query = new URLSearchParams({ subject: route.subject, topic: route.topic })
      return `${course(route.courseId)}/write?${query}`
    }
    case 'material': {
      const material = `${course(route.courseId)}/materials/${encodeURIComponent(route.documentId)}`
      return route.section ? `${material}?section=${route.section}` : material
    }
    case 'topic':
      return `${course(route.courseId)}/topics/${encodeURIComponent(route.subject)}/${encodeURIComponent(route.topic)}`
    case 'papers':
      return '#/papers'
    case 'collection':
      return collection(route.collectionId)
    case 'collection-members':
      return `${collection(route.collectionId)}/members`
    case 'paper': {
      const paper = `${collection(route.collectionId)}/read/${encodeURIComponent(route.documentId)}`
      return route.section ? `${paper}?section=${route.section}` : paper
    }
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
