import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api.js'
import SearchBar from '../components/SearchBar.jsx'
import Filters from '../components/Filters.jsx'
import DocumentCard from '../components/DocumentCard.jsx'
import Breadcrumb from '../components/Breadcrumb.jsx'
import { CardSkeleton } from '../components/PageSkeleton.jsx'
import {
  DOC_TYPE_LABELS, SECTION_LEVEL_LABELS, formatSectionLabel,
} from '../labels.js'

export default function Search() {
  const [params, setParams] = useSearchParams()
  const [results, setResults] = useState({ total: 0, items: [] })
  const [sectionResults, setSectionResults] = useState({ total: 0, items: [] })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [topics, setTopics] = useState([])
  const mode = params.get('mode') || 'dokumenti'

  const current = Object.fromEntries(params.entries())

  useEffect(() => {
    api.listTopics().then(setTopics).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    if (mode === 'apakspunkti') {
      if (!current.q || current.q.length < 2) {
        setSectionResults({ total: 0, items: [] })
        setLoading(false)
        return
      }
      api.searchSections({ q: current.q, limit: 50 })
        .then(setSectionResults)
        .catch((e) => {
          setSectionResults({ total: 0, items: [] })
          setError(e.message || 'Nezināma kļūda')
        })
        .finally(() => setLoading(false))
    } else {
      const { mode: _, ...rest } = current
      api.listDocuments({ ...rest, limit: 50 })
        .then(setResults)
        .catch((e) => {
          setResults({ total: 0, items: [] })
          setError(e.message || 'Nezināma kļūda')
        })
        .finally(() => setLoading(false))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.toString()])

  const updateFilters = (next) => {
    const q = current.q
    const merged = q ? { ...next, q } : next
    if (mode === 'apakspunkti') merged.mode = 'apakspunkti'
    setParams(
      Object.fromEntries(Object.entries(merged).filter(([_, v]) => v))
    )
  }

  const onSearch = (q) => {
    const next = { ...current, ...(q ? { q } : {}) }
    if (!q) delete next.q
    if (mode === 'apakspunkti') next.mode = 'apakspunkti'
    setParams(next)
  }

  const setMode = (newMode) => {
    const next = { ...current, mode: newMode }
    if (newMode === 'dokumenti') delete next.mode
    setParams(next)
  }

  return (
    <div className="animate-fade-in">
      <Breadcrumb items={[{ label: 'Sākums', to: '/' }, { label: 'Meklēšana' }]} />
      <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">Meklēšana</h1>
      <SearchBar value={current.q || ''} onSubmit={onSearch} />

      <div className="mt-5 inline-flex rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-100/70 dark:bg-slate-900/60 p-1">
        <ModeTab active={mode === 'dokumenti'} onClick={() => setMode('dokumenti')}>
          Dokumenti
        </ModeTab>
        <ModeTab active={mode === 'apakspunkti'} onClick={() => setMode('apakspunkti')}>
          Panti / apakšpunkti
        </ModeTab>
      </div>

      {error && <ApiErrorBanner message={error} />}

      {mode === 'dokumenti' ? (
        <div className="grid md:grid-cols-[260px_1fr] gap-6 mt-6">
          <Filters value={current} onChange={updateFilters} topics={topics} />
          <div>
            <div className="text-sm text-slate-500 dark:text-slate-400 mb-3">
              {loading
                ? 'Meklē…'
                : <><span className="font-semibold text-slate-700 dark:text-slate-200">{results.total}</span> {results.total === 1 ? 'dokuments' : 'dokumenti'}</>}
            </div>
            {loading ? (
              <div className="grid gap-3">
                {Array.from({ length: 3 }).map((_, i) => <CardSkeleton key={i} />)}
              </div>
            ) : results.items.length === 0 && !error ? (
              <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/50 p-8 text-center">
                <div className="text-3xl mb-2">🔍</div>
                <p className="text-slate-600 dark:text-slate-400">
                  Nav rezultātu šai meklēšanai.
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Mēģiniet plašāku vaicājumu vai noņemiet kādu filtru.
                </p>
              </div>
            ) : (
              <div className="grid gap-3">
                {results.items.map((doc) => <DocumentCard key={doc.id} doc={doc} />)}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="mt-6">
          <div className="text-sm text-slate-500 dark:text-slate-400 mb-3">
            {loading
              ? 'Meklē…'
              : current.q
                ? <><span className="font-semibold text-slate-700 dark:text-slate-200">{sectionResults.total}</span> {sectionResults.total === 1 ? 'pants/punkts' : 'panti/punkti'}</>
                : 'Ievadiet meklēšanas vaicājumu, lai sāktu meklēt pantu/punktu līmenī.'}
          </div>
          {loading ? (
            <div className="grid gap-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="skeleton h-20 rounded-lg" />
              ))}
            </div>
          ) : sectionResults.items.length === 0 && current.q && !error ? (
            <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/50 p-8 text-center">
              <div className="text-3xl mb-2">📄</div>
              <p className="text-slate-600 dark:text-slate-400">
                Nav pantu/punktu, kas atbilstu vaicājumam.
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Mēģiniet plašāku meklējumu (piem., "darba" vai "5. pants").
              </p>
            </div>
          ) : (
            <div className="grid gap-2">
              {sectionResults.items.map((hit) => (
                <SectionHit key={hit.id} hit={hit} />
              ))}
            </div>
          )}
          <p className="text-xs text-slate-500 mt-4">
            Meklē pēc panta/punkta numura, virsraksta un īsa fragmenta.
            Autoritatīvais teksts vienmēr atrodas oficiālajā avotā.
          </p>
        </div>
      )}
    </div>
  )
}

function ApiErrorBanner({ message }) {
  const looksLikeNetwork = /fetch|network|failed|load/i.test(message)
  return (
    <div className="mt-4 rounded-xl border border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-900/30 p-4 text-sm text-rose-800 dark:text-rose-200 shadow-soft">
      <div className="font-semibold mb-1">⚠ Meklēšana neizdevās</div>
      <div className="font-mono text-xs mb-2 break-all">{message}</div>
      {looksLikeNetwork ? (
        <div>
          Izskatās, ka backend nav sasniedzams. Pārbaudi, vai{' '}
          <code className="bg-rose-100 dark:bg-rose-950 px-1 rounded font-mono">uvicorn app.main:app --reload</code>{' '}
          darbojas mapē <code className="bg-rose-100 dark:bg-rose-950 px-1 rounded font-mono">backend/</code>{' '}
          un ka tas klausās uz <code className="bg-rose-100 dark:bg-rose-950 px-1 rounded font-mono">localhost:8000</code>.
        </div>
      ) : (
        <div>
          Pārbaudi backend konsoli. Ja nesen mainījās datubāzes shēma, iespējams,
          vajag pārstartēt uvicorn vai izdzēst veco{' '}
          <code className="font-mono">backend/data.db</code> un palaist{' '}
          <code className="bg-rose-100 dark:bg-rose-950 px-1 rounded font-mono">python seed_data.py</code>.
        </div>
      )}
    </div>
  )
}

function ModeTab({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={
        'px-4 py-1.5 text-sm font-medium rounded-md transition-all ' +
        (active
          ? 'bg-white dark:bg-slate-800 text-brand-700 dark:text-brand-300 shadow-soft'
          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200')
      }
    >
      {children}
    </button>
  )
}

function SectionHit({ hit }) {
  return (
    <div className="rounded-xl border border-slate-200/70 dark:border-slate-800 p-3 bg-white/90 dark:bg-slate-900/70 shadow-soft hover:shadow-lift hover:border-brand-300 transition-all">
      <div className="flex items-center gap-2 flex-wrap text-xs text-slate-500 dark:text-slate-400">
        <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300">
          {SECTION_LEVEL_LABELS[hit.level] || hit.level}
        </span>
        <Link
          to={`/dokuments/${hit.document_id}`}
          className="hover:underline truncate max-w-[60%]"
          title={hit.document_title}
        >
          {DOC_TYPE_LABELS[hit.document_type] || hit.document_type}: {hit.document_title}
        </Link>
      </div>
      <div className="mt-1 font-medium">
        <a
          href={hit.deep_link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-brand-700 dark:text-brand-400 hover:underline"
          title="Atvērt oficiālajā avotā"
        >
          {formatSectionLabel(hit)}
        </a>
        {hit.title && <span className="text-slate-700 dark:text-slate-300"> — {hit.title}</span>}
      </div>
      {hit.snippet && (
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{hit.snippet}</p>
      )}
      {hit.breadcrumb && hit.breadcrumb.length > 0 && (
        <div className="text-[11px] text-slate-400 mt-1">
          {hit.breadcrumb.join(' › ')}
        </div>
      )}
    </div>
  )
}
