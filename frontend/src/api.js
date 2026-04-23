// Plāns fetch wrapper — MVP bez atsevišķas bibliotēkas.
// Iekļauj vieglu in-memory keša slāni taksonomijām, stats un suggest.

const BASE = import.meta.env.VITE_API_URL || '/api'

// ---- Cache ----
const cache = new Map() // key -> { expires: ms, value }

function cacheGet(key) {
  const entry = cache.get(key)
  if (!entry) return null
  if (Date.now() > entry.expires) { cache.delete(key); return null }
  return entry.value
}
function cacheSet(key, value, ttlMs) {
  cache.set(key, { value, expires: Date.now() + ttlMs })
}

// ---- Request ----
async function request(path, params, { signal } = {}) {
  let url = BASE + path
  if (params) {
    const search = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        search.append(k, v)
      }
    })
    const qs = search.toString()
    if (qs) url += '?' + qs
  }
  const resp = await fetch(url, { signal })
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${resp.statusText}`)
  }
  return resp.json()
}

// Cached helper — apvieno vairākus vienlaicīgus pieprasījumus vienā.
const inflight = new Map()
async function cachedRequest(key, loader, ttlMs) {
  const hit = cacheGet(key)
  if (hit !== null) return hit
  if (inflight.has(key)) return inflight.get(key)
  const p = loader()
    .then((val) => { cacheSet(key, val, ttlMs); inflight.delete(key); return val })
    .catch((e) => { inflight.delete(key); throw e })
  inflight.set(key, p)
  return p
}

const FIVE_MIN = 5 * 60 * 1000
const FIFTEEN_SEC = 15 * 1000
const HALF_MIN = 30 * 1000

export const api = {
  listDocuments: (params) => request('/documents', params),

  getDocument: (id) => cachedRequest(
    `doc:${id}`,
    () => request(`/documents/${id}`),
    HALF_MIN,
  ),

  listSources:   () => cachedRequest('sources',   () => request('/sources'),   FIVE_MIN),
  listTopics:    () => cachedRequest('topics',    () => request('/topics'),    FIVE_MIN),
  listDocTypes:  () => cachedRequest('doc-types', () => request('/doc-types'), FIVE_MIN),
  listStatuses:  () => cachedRequest('statuses',  () => request('/statuses'),  FIVE_MIN),
  getStats:      () => cachedRequest('stats',     () => request('/stats'),     FIVE_MIN),

  getSections: (docId) => cachedRequest(
    `sections:${docId}`,
    () => request(`/documents/${docId}/sections`),
    FIVE_MIN,
  ),

  searchSections: (params) => request('/sections/search', params),

  suggest: (q, signal) => {
    const key = `suggest:${q.toLowerCase()}`
    const hit = cacheGet(key)
    if (hit) return Promise.resolve(hit)
    return request('/suggest', { q, limit: 5 }, { signal })
      .then((val) => { cacheSet(key, val, FIFTEEN_SEC); return val })
  },

  prefetchDocument: (id) => cachedRequest(
    `doc:${id}`,
    () => request(`/documents/${id}`),
    HALF_MIN,
  ),

  runImport: async (source, params = {}) => {
    const search = new URLSearchParams(params)
    const resp = await fetch(`${BASE}/import/${source}?${search.toString()}`, {
      method: 'POST',
    })
    if (!resp.ok) throw new Error(`Import ${resp.status}`)
    return resp.json()
  },

  _clearCache: () => cache.clear(),
}
