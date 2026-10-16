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
  if (health.status === 'ok') return <p role="status">Platform connected</p>

  const notServing = Object.entries(health.services)
    .filter(([, status]) => status !== 'SERVING')
    .map(([name]) => name)
  return (
    <p role="status">
      Platform degraded: {health.error ?? `not serving: ${notServing.join(', ')}`}
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
