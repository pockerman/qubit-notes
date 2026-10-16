import { useState, type FormEvent } from 'react'

export function SignIn({ onSignIn }: { onSignIn: (student: string) => void }) {
  const [name, setName] = useState('')

  function submit(event: FormEvent) {
    event.preventDefault()
    if (name.trim()) onSignIn(name.trim())
  }

  return (
    <form className="card sign-in" onSubmit={submit}>
      <h2>Sign in</h2>
      <label>
        Your name
        <input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
      </label>
      <button type="submit">Sign in</button>
    </form>
  )
}
