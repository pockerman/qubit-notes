import type { AuthConfig, Identity } from './auth'
export type Health = {
  status: 'ok' | 'degraded'
  // platform service name to its status, e.g. SERVING or NOT_SERVING
  services: Record<string, string>
  error: string | null
}

export type Role = 'owner' | 'reader'

export type Course = {
  id: string
  name: string
  owner: string
  role: Role
}

export type Member = {
  student: string
  role: Role
}

export type IngestStatus = 'pending' | 'running' | 'completed' | 'failed'

export type Material = {
  document_id: string
  course: string
  course_id: string
  subject: string
  topic: string
  filename: string
  status: IngestStatus
  kind: 'text' | 'video'
  duration_seconds: number | null
  // what a PDF or an EPUB was converted from, to Markdown; its original can be downloaded too
  converted_from: 'pdf' | 'epub' | null
  // why it could not be processed, e.g. a PDF without text
  error: string | null
}

export type Topic = {
  subject: string
  topic: string
  // how many materials it has
  materials: number
}

export type Upload = {
  job_id: string
  document_id: string
  course_id: string
  status: IngestStatus
  // the references of a Markdown material to what its course doesn't have, as written
  broken_references: string[]
}

/** A reference in a Markdown material to a topic, a material or a section of its course, e.g. [[subject/topic]]. */
export type Reference = {
  // as written, e.g. "[[numerical-methods/finite-elements|the FEM topic]]"
  written: string
  shown_as: string
  // 'nothing' if the course doesn't have what it refers to: the reference is broken
  refers_to: 'topic' | 'material' | 'section' | 'nothing'
  subject: string | null
  topic: string | null
  material: string | null
  document_id: string | null
  section: string | null
  // the section's position in its material, to open it there
  position: number | null
}

/** A material that refers to a topic. */
export type Mention = {
  subject: string
  topic: string
  material: string
  document_id: string
}

export type TopicMentions = {
  subject: string
  topic: string
  mentioned_in: Mention[]
}

export type IngestJob = {
  job_id: string
  document_id: string
  status: IngestStatus
  error: string | null
}

export type Section = {
  position: number
  // empty for text before a document's first heading
  title: string
  // 1 for a chapter, 2 for a heading within it, and so on
  level: number
  page_start: number | null
  page_end: number | null
}

export type SectionText = {
  section: Section
  // the section's own text, without its subsections'
  content: string
}

export type OpenedMaterial = {
  course_id: string
  document_id: string
  filename: string
  subject: string
  topic: string
  kind: 'text' | 'video'
  content_type: string
  duration_seconds: number | null
  converted_from: 'pdf' | 'epub' | null
  sections: Section[]
}

export type Note = {
  id: string
  course_id: string
  document_id: string
  // on a text
  section: number | null
  section_title: string | null
  passage: string | null
  // on a video
  at_seconds: number | null
  text: string
  created_at: string
  updated_at: string
}

export type NewNote = { text: string } & (
  | { section: number; passage: string }
  | { at_seconds: number }
)

/** What a summary or quiz is about: a section of a document, a whole document, or a topic. */
export type Scope = {
  course_id: string
  document_id?: string | null
  section?: number | null
  subject?: string | null
  topic?: string | null
}

export type Source = {
  document_id: string
  filename: string
  section: number
  title: string
}

export type OutOfDate = { added: string[]; removed: string[]; edited: string[] }

export type Summary = {
  id: string
  scope: Scope
  content: string
  sources: Source[]
  created_at: string
  out_of_date: OutOfDate | null
}

export type Question = {
  question: string
  choices: string[]
  source: Source
}

export type Quiz = {
  id: string
  scope: Scope
  questions: Question[]
  sources: Source[]
  created_at: string
  out_of_date: OutOfDate | null
}

export type QuestionResult = {
  question: string
  chosen: number | null
  correct: boolean
  correct_choice: number
  source: Source
}

export type Attempt = {
  id: string
  quiz_id: string
  score: number
  total: number
  results: QuestionResult[]
  created_at: string
}

/** What the student asked the assistant, and its reply: an answer citing sections, a summary or a quiz. */
export type Turn = {
  id: string
  question: string
  kind: 'answer' | 'summary' | 'quiz'
  // an answer's text; for a summary or a quiz, what the assistant says of it
  answer: string
  // whether the material covers the question
  covered: boolean
  sources: Source[]
  // null once deleted with their material
  summary: Summary | null
  quiz: Quiz | null
  created_at: string
}

export type Conversation = {
  id: string | null
  turns: Turn[]
}

function scopeQuery(scope: Scope): string {
  const entries = Object.entries(scope).filter(([, value]) => value !== null && value !== undefined)
  return new URLSearchParams(entries.map(([key, value]) => [key, String(value)])).toString()
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

/** The images a Markdown material refers to, by the paths it refers to them by. */
export type MaterialImages = {
  images: string[]
  missing: string[]
}

/** How the backend signs students in; asked before anyone has. */
export async function authConfig(): Promise<AuthConfig> {
  const response = await fetch('/api/config')
  if (!response.ok) throw new ApiError(response.status, response.statusText)
  return response.json()
}

/** Calls the backend as a student: who they say they are, or who their Cognito sign-in says (see auth.ts). */
export class StudyApi {
  private readonly identity: Identity

  constructor(identity: Identity) {
    this.identity = identity
  }

  get student(): string {
    return this.identity.student
  }

  private async fetch(path: string, init: RequestInit = {}): Promise<Response> {
    const response = await fetch(`/api${path}`, {
      ...init,
      headers: { ...(await this.identity.headers()), ...init.headers },
    })
    if (response.status === 401) this.identity.refused()
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      const detail = typeof body.detail === 'string' ? body.detail : response.statusText
      throw new ApiError(response.status, detail)
    }
    return response
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    return (await this.fetch(path, init)).json()
  }

  private materialPath(courseId: string, documentId: string): string {
    return `/courses/${encodeURIComponent(courseId)}/materials/${encodeURIComponent(documentId)}`
  }

  openMaterial(courseId: string, documentId: string): Promise<OpenedMaterial> {
    return this.request(this.materialPath(courseId, documentId))
  }

  /** The section at the position, followed by its subsections. */
  readSection(courseId: string, documentId: string, position: number): Promise<SectionText[]> {
    return this.request(`${this.materialPath(courseId, documentId)}/sections/${position}`)
  }

  /** The file's address for a <video> element, which can't send headers: who the student is goes in it. */
  fileUrl(courseId: string, documentId: string): string {
    const query = new URLSearchParams({ ...this.identity.linkQuery(), inline: 'true' })
    return `/api${this.materialPath(courseId, documentId)}/file?${query}`
  }

  notes(courseId: string, documentId: string): Promise<Note[]> {
    return this.request(`${this.materialPath(courseId, documentId)}/notes`)
  }

  addNote(courseId: string, documentId: string, note: NewNote): Promise<Note> {
    return this.request(`${this.materialPath(courseId, documentId)}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(note),
    })
  }

  changeNote(noteId: string, text: string): Promise<Note> {
    return this.request(`/notes/${encodeURIComponent(noteId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
  }

  async deleteNote(noteId: string): Promise<void> {
    await this.fetch(`/notes/${encodeURIComponent(noteId)}`, { method: 'DELETE' })
  }

  /** Asks the assistant, while reading `where`: a section of a material, or a topic. */
  ask(where: Scope, question: string): Promise<Turn> {
    return this.request('/assistant/requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...where, question }),
    })
  }

  /** The conversation with the assistant on the material or the topic of `where`. */
  conversation(where: Scope): Promise<Conversation> {
    return this.request(`/assistant/conversation?${scopeQuery(where)}`)
  }

  /** Forgets the conversation, so the next question starts a new one. */
  startAgain(where: Scope): Promise<Conversation> {
    return this.request(`/assistant/conversation?${scopeQuery(where)}`, { method: 'DELETE' })
  }

  takeQuiz(quizId: string, answers: (number | null)[]): Promise<Attempt> {
    return this.request(`/quizzes/${encodeURIComponent(quizId)}/attempts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    })
  }

  attempts(quizId: string): Promise<Attempt[]> {
    return this.request(`/quizzes/${encodeURIComponent(quizId)}/attempts`)
  }

  /** The uploaded file; the student's header can't go on a plain link, so it's fetched. */
  async download(courseId: string, documentId: string): Promise<Blob> {
    return (await this.fetch(`${this.materialPath(courseId, documentId)}/file`)).blob()
  }

  /** A material converted from a PDF or an EPUB as it is now, as a PDF or an EPUB laid out anew. */
  async export(courseId: string, documentId: string): Promise<Blob> {
    return (await this.fetch(`${this.materialPath(courseId, documentId)}/export`)).blob()
  }

  health(): Promise<Health> {
    return this.request('/health')
  }

  courses(): Promise<Course[]> {
    return this.request('/courses')
  }

  createCourse(name: string): Promise<Course> {
    return this.request('/courses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    })
  }

  topics(course: string): Promise<Topic[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/topics`)
  }

  createTopic(course: string, subject: string, topic: string): Promise<Topic> {
    return this.request(`/courses/${encodeURIComponent(course)}/topics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject, topic }),
    })
  }

  /** The text of a Markdown or text material, to edit. */
  async materialText(courseId: string, documentId: string): Promise<string> {
    const body: { text: string } = await this.request(`${this.materialPath(courseId, documentId)}/text`)
    return body.text
  }

  /** Gives the material new text, which is processed again. */
  editMaterial(courseId: string, documentId: string, text: string): Promise<Upload> {
    return this.request(`${this.materialPath(courseId, documentId)}/text`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
  }

  /** the references of a Markdown material, and what each refers to */
  references(courseId: string, documentId: string): Promise<Reference[]> {
    return this.request(`${this.materialPath(courseId, documentId)}/references`)
  }

  /** the references of text not saved yet, e.g. one being written, and what each refers to */
  referencesIn(courseId: string, text: string): Promise<Reference[]> {
    return this.request(`/courses/${encodeURIComponent(courseId)}/references`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
  }

  /** each topic of the course with the materials it is mentioned in */
  mentions(course: string): Promise<TopicMentions[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/mentions`)
  }

  materials(course: string): Promise<Material[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/materials`)
  }

  private imagesPath(courseId: string, documentId: string): string {
    return `${this.materialPath(courseId, documentId)}/images`
  }

  /** the images a Markdown material refers to: those it has, and those still to be added */
  images(courseId: string, documentId: string): Promise<MaterialImages> {
    return this.request(this.imagesPath(courseId, documentId))
  }

  /** keeps an image with a material, under `path` or the path the material refers to by the image's file name */
  addImage(courseId: string, documentId: string, file: File, path?: string): Promise<MaterialImages> {
    const form = new FormData()
    form.append('file', file)
    if (path) form.append('path', path)
    return this.request(this.imagesPath(courseId, documentId), { method: 'POST', body: form })
  }

  async image(courseId: string, documentId: string, path: string): Promise<Blob> {
    const encoded = path.split('/').map(encodeURIComponent).join('/')
    return (await this.fetch(`${this.imagesPath(courseId, documentId)}/${encoded}`)).blob()
  }

  /** a Markdown material the student wrote in a topic; it's processed like an upload */
  writeMaterial(course: string, subject: string, topic: string, name: string, text: string): Promise<Upload> {
    const [c, s, t] = [course, subject, topic].map(encodeURIComponent)
    return this.request(`/courses/${c}/subjects/${s}/topics/${t}/materials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, text }),
    })
  }

  upload(location: string, file: File): Promise<Upload> {
    const form = new FormData()
    form.append('location', location)
    form.append('file', file)
    return this.request('/materials', { method: 'POST', body: form })
  }

  uploadStatus(jobId: string): Promise<IngestJob> {
    return this.request(`/uploads/${encodeURIComponent(jobId)}`)
  }

  deleteMaterial(material: Material): Promise<Material> {
    const path = [material.course, material.subject, material.topic, material.filename].map(encodeURIComponent)
    return this.request(`/courses/${path[0]}/materials/${path.slice(1).join('/')}`, { method: 'DELETE' })
  }

  /** deletes the topic with all of its material */
  async deleteTopic(course: string, subject: string, topic: string): Promise<void> {
    const [c, s, t] = [course, subject, topic].map(encodeURIComponent)
    await this.fetch(`/courses/${c}/subjects/${s}/topics/${t}`, { method: 'DELETE' })
  }

  /** puts the subject's topics in the order they're meant to be read; returns the course's topics */
  orderTopics(course: string, subject: string, topics: string[]): Promise<Topic[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/subjects/${encodeURIComponent(subject)}/topic-order`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topics }),
    })
  }

  async deleteCourse(course: string): Promise<void> {
    await this.fetch(`/courses/${encodeURIComponent(course)}`, { method: 'DELETE' })
  }

  members(course: string): Promise<Member[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/members`)
  }

  share(course: string, student: string, role: Role): Promise<Member[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/members`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student, role }),
    })
  }

  unshare(course: string, student: string): Promise<Member[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/members/${encodeURIComponent(student)}`, {
      method: 'DELETE',
    })
  }
}

/** Waits until the upload has been processed, or has failed. */
export async function waitForUpload(api: StudyApi, jobId: string, intervalMs = 1000): Promise<IngestJob> {
  for (;;) {
    const job = await api.uploadStatus(jobId)
    if (job.status === 'completed' || job.status === 'failed') return job
    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }
}
