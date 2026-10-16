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
  subject: string
  topic: string
  filename: string
  status: IngestStatus
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

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(`/api${path}`, {
      ...init,
      headers: { 'X-Student-Id': this.student, ...init.headers },
    })
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      const detail = typeof body.detail === 'string' ? body.detail : response.statusText
      throw new ApiError(response.status, detail)
    }
    return response.json()
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
