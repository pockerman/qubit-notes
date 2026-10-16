export type Health = {
  status: 'ok' | 'degraded'
  // platform service name to its status, e.g. SERVING or NOT_SERVING
  services: Record<string, string>
  error: string | null
}

export async function getHealth(): Promise<Health> {
  const response = await fetch('/api/health')
  if (!response.ok) throw new Error(`health check failed: ${response.status}`)
  return response.json()
}
