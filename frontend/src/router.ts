import { useEffect, useState } from 'react'

/**
 * The page shown, from the address's hash, so the browser's back button and a refresh keep the student where
 * they were:
 *   #/                                     my courses
 *   #/reviews                              the flashcards due for review
 *   #/settings                             the app's settings: the AI's model
 *   #/settings/account                     the student's account: their email and password
 *   #/courses/<id>                         a course
 *   #/courses/<id>/subjects/<subject>      a subject: its topics
 *   #/courses/<id>/add?subject=…&topic=…   adding material to it
 *   #/courses/<id>/write?subject=…&topic=… writing material in a topic
 *   #/courses/<id>/generate?subject=…&topic=…  the AI writing material from a topic's
 *   #/courses/<id>/members                 who it is shared with
 *   #/courses/<id>/materials/<document>    reading a material
 *   #/courses/<id>/materials/<document>?section=<position>  reading it at a section
 *   #/courses/<id>/topics/<subject>/<topic> a topic: its material, and the assistant on all of it
 */
// the settings' views, under Settings in the app's menu
export type SettingsView = 'ai-model' | 'account'

export type Route =
  | { page: 'courses' }
  | { page: 'reviews' }
  | { page: 'settings'; view: SettingsView }
  | { page: 'course'; courseId: string }
  | { page: 'subject'; courseId: string; subject: string }
  | { page: 'add'; courseId: string; subject: string; topic: string }
  | { page: 'members'; courseId: string }
  | { page: 'write'; courseId: string; subject: string; topic: string }
  | { page: 'generate'; courseId: string; subject: string; topic: string }
  | { page: 'material'; courseId: string; documentId: string; section?: number }
  | { page: 'topic'; courseId: string; subject: string; topic: string }

export function parse(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?')
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent)
  const params = new URLSearchParams(query)
  if (parts[0] === 'reviews') return { page: 'reviews' }
  if (parts[0] === 'settings') return { page: 'settings', view: parts[1] === 'account' ? 'account' : 'ai-model' }
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
  switch (route.page) {
    case 'courses':
      return '#/'
    case 'reviews':
      return '#/reviews'
    case 'settings':
      return route.view === 'account' ? '#/settings/account' : '#/settings'
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
