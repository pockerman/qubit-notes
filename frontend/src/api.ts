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
}

export type Upload = {
  job_id: string
  document_id: string
  course_id: string
  status: IngestStatus
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

export type OutOfDate = { added: string[]; removed: string[] }

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

/** Calls the backend as a student; there is no authentication yet, the student says who they are. */
export class StudyApi {
  readonly student: string

  constructor(student: string) {
    this.student = student
  }

  private async fetch(path: string, init: RequestInit = {}): Promise<Response> {
    const response = await fetch(`/api${path}`, {
      ...init,
      headers: { 'X-Student-Id': this.student, ...init.headers },
    })
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

  /** The file's address for a <video> element, which can't send the student's header. */
  fileUrl(courseId: string, documentId: string): string {
    const query = new URLSearchParams({ student: this.student, inline: 'true' })
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

  /** The newest saved summary of the scope, or a new one if there's none or `fresh`. */
  summary(scope: Scope, fresh = false): Promise<Summary> {
    return this.request('/summaries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...scope, new: fresh }),
    })
  }

  summaries(scope: Scope): Promise<Summary[]> {
    return this.request(`/summaries?${scopeQuery(scope)}`)
  }

  /** The newest saved quiz of the scope and size, or a new one if there's none or `fresh`. */
  quiz(scope: Scope, questions: number, fresh = false): Promise<Quiz> {
    return this.request('/quizzes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...scope, questions, new: fresh }),
    })
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

  health(): Promise<Health> {
    return this.request('/health')
  }

  courses(): Promise<Course[]> {
    return this.request('/courses')
  }

  materials(course: string): Promise<Material[]> {
    return this.request(`/courses/${encodeURIComponent(course)}/materials`)
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
