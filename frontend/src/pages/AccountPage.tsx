import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Account, StudyApi } from '../api'
import { href } from '../router'

// what the student is told, as a sentence
const sentence = (text: string) => text.charAt(0).toUpperCase() + text.slice(1).replace(/\.?$/, '.')

/** The student's account: their email and password, which Cognito keeps and the app changes through it; signed in
 * by name, there are none (features/ui_account.feature). */
export function AccountPage({ api }: { api: StudyApi }) {
  const [account, setAccount] = useState<Account | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.account().then(setAccount, (e: Error) => setError(sentence(e.message)))
  }, [api])

  useEffect(load, [load])

  return (
    <section className="settings" aria-labelledby="settings-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'courses' })}>
          ← My courses
        </a>
        <h2 id="settings-title">Settings</h2>
      </header>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {account && (
        <section className="card" aria-labelledby="account-title">
          <h3 id="account-title">Account</h3>
          {account.signs_in_with === 'name' ? (
            <p className="note">You sign in by name here, so there is no email or password to change.</p>
          ) : (
            <>
              <EmailForm api={api} email={account.email} onChanged={load} />
              <PasswordForm api={api} />
            </>
          )}
        </section>
      )}
    </section>
  )
}

type EmailFormProps = { api: StudyApi; email: string | null; onChanged: () => void }

/** A new email, used once it is confirmed with the code Cognito emails to it. */
function EmailForm({ api, email, onChanged }: EmailFormProps) {
  const [newEmail, setNewEmail] = useState('')
  // the email a code was sent to, until it is confirmed
  const [confirming, setConfirming] = useState<string | null>(null)
  const [code, setCode] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null)

  async function change(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setMessage(null)
    try {
      await api.changeEmail(newEmail)
      setConfirming(newEmail.trim())
      setNewEmail('')
    } catch (e) {
      setMessage({ text: sentence((e as Error).message), error: true })
    }
    setSaving(false)
  }

  async function confirm(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setMessage(null)
    try {
      await api.confirmEmail(code)
      setConfirming(null)
      setCode('')
      setMessage({ text: 'Your email is changed.' })
      onChanged()
    } catch (e) {
      setMessage({ text: sentence((e as Error).message), error: true })
    }
    setSaving(false)
  }

  return (
    <div className="account-part">
      <h4>Email</h4>
      <p>
        Your email is <strong>{email ?? 'not set'}</strong>.
      </p>
      {confirming === null ? (
        <form aria-label="Change my email" onSubmit={change}>
          <label>
            New email
            <input type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} required />
          </label>
          <div className="actions">
            <button type="submit" disabled={saving || !newEmail.trim()}>
              {saving ? 'Saving…' : 'Change email'}
            </button>
          </div>
        </form>
      ) : (
        <form aria-label="Confirm my email" onSubmit={confirm}>
          <p>Enter the code sent to {confirming}. Until then, your email stays as it is.</p>
          <label>
            Code
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              inputMode="numeric"
              autoComplete="one-time-code"
              required
            />
          </label>
          <div className="actions">
            <button type="submit" disabled={saving || !code.trim()}>
              {saving ? 'Confirming…' : 'Confirm'}
            </button>
            <button type="button" className="link" onClick={() => setConfirming(null)}>
              Cancel
            </button>
          </div>
        </form>
      )}
      {message && (
        <p role={message.error ? 'alert' : 'status'} className={message.error ? 'error' : 'note'}>
          {message.text}
        </p>
      )}
    </div>
  )
}

/** A new password, given twice, with the current one. */
function PasswordForm({ api }: { api: StudyApi }) {
  const [current, setCurrent] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [again, setAgain] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null)

  async function change(event: FormEvent) {
    event.preventDefault()
    setMessage(null)
    if (newPassword !== again) {
      setMessage({ text: 'The new passwords are not the same.', error: true })
      return
    }
    setSaving(true)
    try {
      await api.changePassword(current, newPassword)
      setCurrent('')
      setNewPassword('')
      setAgain('')
      setMessage({ text: 'Your password is changed.' })
    } catch (e) {
      setMessage({ text: sentence((e as Error).message), error: true })
    }
    setSaving(false)
  }

  return (
    <div className="account-part">
      <h4>Password</h4>
      <form aria-label="Change my password" onSubmit={change}>
        <label>
          Current password
          <input
            type="password"
            autoComplete="current-password"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            required
          />
        </label>
        <label>
          New password
          <input
            type="password"
            autoComplete="new-password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
        </label>
        <label>
          New password again
          <input
            type="password"
            autoComplete="new-password"
            value={again}
            onChange={(e) => setAgain(e.target.value)}
            required
          />
        </label>
        <p className="note">At least 12 characters, with a lower case letter, a capital and a digit</p>
        <div className="actions">
          <button type="submit" disabled={saving || !current || !newPassword || !again}>
            {saving ? 'Saving…' : 'Change password'}
          </button>
        </div>
      </form>
      {message && (
        <p role={message.error ? 'alert' : 'status'} className={message.error ? 'error' : 'note'}>
          {message.text}
        </p>
      )}
    </div>
  )
}
