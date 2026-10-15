import { useEffect, useState } from 'react'
import { getHealth, type Health } from './api'

function PlatformStatus() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getHealth().then(setHealth, (e: Error) => setError(e.message))
  }, [])

  if (error) return <p role="status">Backend unreachable: {error}</p>
  if (!health) return <p role="status">Checking the platform…</p>
  return (
    <p role="status">
      Platform {health.status === 'ok' ? 'connected' : `degraded: ${health.error}`}
      {health.providers.length > 0 && ` · providers: ${health.providers.join(', ')}`}
    </p>
  )
}

export default function App() {
  return (
    <main>
      <h1>Study Assistant</h1>
      <PlatformStatus />
    </main>
  )
}
