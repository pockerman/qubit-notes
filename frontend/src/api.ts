export type Health = {
  status: 'ok' | 'degraded'
  providers: string[]
  error: string | null
}

export async function getHealth(): Promise<Health> {
  const response = await fetch('/api/health')
  if (!response.ok) throw new Error(`health check failed: ${response.status}`)
  return response.json()
}
