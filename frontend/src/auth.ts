// Who the student is, as the backend is told it. Run without Cognito, as in development, the student says who they
// are by name. With Cognito, the student signs in on Cognito's pages (OAuth 2 authorization code with PKCE) and
// every request carries their access token; it's refreshed before it expires, and a request refused for it sends
// the student to sign in again.

/** How the backend signs students in, from /api/config. */
export type AuthConfig = { auth: 'name' } | { auth: 'cognito'; cognito: { domain: string; client_id: string } }

export interface Identity {
  readonly student: string
  /** the headers that say who the student is */
  headers(): Promise<Record<string, string>>
  /** what says who the student is in a link, e.g. a <video>'s, which can't send headers */
  linkQuery(): Record<string, string>
  /** the backend didn't take who the student is */
  refused(): void
  signOut(): void
}

const STUDENT_KEY = 'study-assistant.student'
const TOKENS_KEY = 'study-assistant.cognito'
const PENDING_KEY = 'study-assistant.cognito-pending'
// a token is refreshed this long before it expires
const REFRESH_MARGIN_SECONDS = 60

function read(storage: () => Storage, key: string): string | null {
  try {
    return storage().getItem(key)
  } catch {
    return null
  }
}

function write(storage: () => Storage, key: string, value: string | null) {
  try {
    if (value === null) storage().removeItem(key)
    else storage().setItem(key, value)
  } catch {
    // the student signs in again next time
  }
}

const local = () => localStorage
const session = () => sessionStorage

// by name

export function storedStudent(): string | null {
  return read(local, STUDENT_KEY)
}

export function nameIdentity(student: string, onSignOut: () => void): Identity {
  write(local, STUDENT_KEY, student)
  return {
    student,
    headers: async () => ({ 'X-Student-Id': student }),
    linkQuery: () => ({ student }),
    refused: () => {},
    signOut: () => {
      write(local, STUDENT_KEY, null)
      onSignOut()
    },
  }
}

// with Cognito

type CognitoConfig = { domain: string; client_id: string }
type Tokens = { access_token: string; refresh_token?: string }

function claims(token: string): Record<string, unknown> {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(payload.padEnd(payload.length + ((4 - (payload.length % 4)) % 4), '=')))
  } catch {
    return {}
  }
}

function base64url(bytes: ArrayBuffer | Uint8Array): string {
  const array = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes)
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
}

function randomText(): string {
  return base64url(crypto.getRandomValues(new Uint8Array(32)))
}

// Cognito sends the student back to the app's own address
const redirectUri = () => `${window.location.origin}/`

/** Sends the browser to Cognito's sign-in page. */
export async function startCognitoSignIn(config: CognitoConfig): Promise<void> {
  const verifier = randomText()
  const state = randomText()
  const challenge = base64url(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier)))
  // where the student was going, to go back there once signed in
  write(session, PENDING_KEY, JSON.stringify({ verifier, state, hash: window.location.hash }))
  const query = new URLSearchParams({
    response_type: 'code',
    client_id: config.client_id,
    redirect_uri: redirectUri(),
    scope: 'openid',
    state,
    code_challenge: challenge,
    code_challenge_method: 'S256',
  })
  window.location.assign(`${config.domain}/oauth2/authorize?${query}`)
}

async function tokenRequest(config: CognitoConfig, body: Record<string, string>): Promise<Tokens> {
  const response = await fetch(`${config.domain}/oauth2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: config.client_id, ...body }),
  })
  if (!response.ok) throw new Error(`Cognito did not sign you in (${response.status})`)
  return response.json()
}

/**
 * The tokens Cognito's sign-in page sent the student back with, if it just did: the code in the address is swapped
 * for them, and taken out of the address. Otherwise the tokens kept from before, if any.
 */
export async function cognitoTokens(config: CognitoConfig): Promise<Tokens | null> {
  const query = new URLSearchParams(window.location.search)
  const code = query.get('code')
  if (code) {
    const pending = JSON.parse(read(session, PENDING_KEY) ?? '{}')
    write(session, PENDING_KEY, null)
    window.history.replaceState(null, '', `/${pending.hash ?? ''}`)
    if (!pending.verifier || query.get('state') !== pending.state) throw new Error('The sign-in did not come from here')
    const tokens = await tokenRequest(config, {
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri(),
      code_verifier: pending.verifier,
    })
    write(local, TOKENS_KEY, JSON.stringify(tokens))
    return tokens
  }
  const kept = read(local, TOKENS_KEY)
  return kept ? JSON.parse(kept) : null
}

export function cognitoIdentity(config: CognitoConfig, initial: Tokens): Identity {
  let tokens = initial
  let refreshing: Promise<void> | null = null

  const expiresSoon = () => Number(claims(tokens.access_token).exp ?? 0) - REFRESH_MARGIN_SECONDS < Date.now() / 1000

  async function refresh() {
    if (!tokens.refresh_token) throw new Error('signed out')
    const refreshed = await tokenRequest(config, { grant_type: 'refresh_token', refresh_token: tokens.refresh_token })
    // Cognito keeps the refresh token the same
    tokens = { ...tokens, ...refreshed }
    write(local, TOKENS_KEY, JSON.stringify(tokens))
  }

  function signInAgain() {
    write(local, TOKENS_KEY, null)
    void startCognitoSignIn(config)
  }

  return {
    student: String(claims(initial.access_token).username ?? ''),
    async headers() {
      if (expiresSoon()) {
        refreshing ??= refresh().finally(() => (refreshing = null))
        try {
          await refreshing
        } catch {
          signInAgain()
        }
      }
      return { Authorization: `Bearer ${tokens.access_token}` }
    },
    linkQuery: () => ({ access_token: tokens.access_token }),
    refused: signInAgain,
    signOut() {
      write(local, TOKENS_KEY, null)
      const query = new URLSearchParams({ client_id: config.client_id, logout_uri: redirectUri() })
      window.location.assign(`${config.domain}/logout?${query}`)
    },
  }
}
