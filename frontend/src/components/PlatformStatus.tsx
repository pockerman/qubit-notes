import { useEffect, useState } from 'react'
import type { Health, StudyApi } from '../api'

export function PlatformStatus({ api }: { api: StudyApi }) {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.health().then(setHealth, (e: Error) => setError(e.message))
  }, [api])

  if (error) return <span role="status" className="badge bad">Backend unreachable</span>
  if (!health) return <span role="status" className="badge">Checking the platform…</span>
  if (health.status === 'ok') return <span role="status" className="badge good">Platform connected</span>

  const notServing = Object.entries(health.services)
    .filter(([, status]) => status !== 'SERVING')
    .map(([name]) => name)
  return (
    <span role="status" className="badge bad" title={health.error ?? undefined}>
      Platform degraded{notServing.length > 0 && `: ${notServing.join(', ')}`}
    </span>
  )
}
