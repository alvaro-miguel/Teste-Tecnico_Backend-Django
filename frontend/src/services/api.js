const API_ROOT = import.meta.env.VITE_API_URL || '/api'

const tokenKey = (kind) => `clinica.${kind}`

function extractError(payload, fallback) {
  if (!payload) return fallback
  if (typeof payload === 'string') return payload
  if (Array.isArray(payload)) return payload.map((item) => extractError(item, '')).join(' ')

  const messages = Object.values(payload)
    .flatMap((value) => (Array.isArray(value) ? value : [value]))
    .map((value) => extractError(value, ''))
    .filter(Boolean)

  return messages.join(' ') || fallback
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem(tokenKey('refresh'))
  if (!refresh) return null

  const response = await fetch(`${API_ROOT}/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!response.ok) return null

  const data = await response.json()
  localStorage.setItem(tokenKey('access'), data.access)
  return data.access
}

export async function request(path, options = {}, allowRefresh = true) {
  const headers = new Headers(options.headers || {})
  const access = localStorage.getItem(tokenKey('access'))

  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (access) headers.set('Authorization', `Bearer ${access}`)

  const response = await fetch(`${API_ROOT}${path}`, { ...options, headers })

  if (response.status === 401 && access && allowRefresh) {
    const newAccess = await refreshAccessToken()
    if (newAccess) return request(path, options, false)
  }

  if (response.status === 204) return null

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const error = new Error(extractError(payload, 'Não foi possível concluir a solicitação.'))
    error.status = response.status
    error.payload = payload
    throw error
  }
  return payload
}

export async function listAll(path, maxPages = 20) {
  const items = []
  let next = path
  let page = 0

  while (next && page < maxPages) {
    const normalized = next.startsWith('http') ? new URL(next).pathname + new URL(next).search : next
    const data = await request(normalized.replace(/^\/api/, ''))
    if (Array.isArray(data)) return data
    items.push(...(data.results || []))
    next = data.next
    page += 1
  }
  return items
}

export { API_ROOT }
