import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import SearchBar from '../components/SearchBar.jsx'
import DocumentCard from '../components/DocumentCard.jsx'
import { CardSkeleton } from '../components/PageSkeleton.jsx'
import { TOPIC_LABELS, TOPIC_ICONS } from '../labels.js'

export default function Dashboard() {
  const [recent, setRecent] = useState([])
  const [topics, setTopics] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      api.listDocuments({ limit: 6 }),
      api.listTopics(),
    ]).then(([docs, t]) => {
      setRecent(docs.items)
      setTopics(t)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-10 animate-fade-in">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-200/70 dark:border-slate-800 bg-gradient-to-br from-white via-brand-50/40 to-white dark:from-slate-900 dark:via-brand-950/40 dark:to-slate-900 px-6 py-10 md:px-10 md:py-14 shadow-soft">
        <div aria-hidden className="pointer-events-none absolute -top-24 -right-20 h-64 w-64 rounded-full bg-brand-300/30 dark:bg-brand-600/20 blur-3xl" />
        <div aria-hidden className="pointer-events-none absolute -bottom-20 -left-16 h-56 w-56 rounded-full bg-brand-500/20 dark:bg-brand-800/30 blur-3xl" />

        <div className="relative max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-600/10 dark:bg-brand-500/15 text-brand-700 dark:text-brand-300 text-xs font-semibold mb-4">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-500 animate-pulse-soft" />
            MVP · oficiālo datu pārlūks
          </div>
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 dark:text-slate-50 mb-3">
            Latvijas tiesību akti un
            <span className="block bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
              atvērtie dati vienuviet
            </span>
          </h1>
          <p className="text-slate-600 dark:text-slate-300 mb-6 md:text-lg max-w-2xl">
            Meklē likumus, MK noteikumus, vadlīnijas un datu kopas ar reāllaika ieteikumiem.
            Katram ierakstam ir tieša saite uz oficiālo publikāciju.
          </p>
          <SearchBar onSubmit={(q) => navigate(`/meklet?q=${encodeURIComponent(q)}`)} />
          <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span className="opacity-70">Mēģini:</span>
            {['PVN', 'darba likums', 'datu aizsardzība', 'muita'].map((q) => (
              <button
                key={q}
                onClick={() => navigate(`/meklet?q=${encodeURIComponent(q)}`)}
                className="px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 hover:border-brand-400 hover:text-brand-700 dark:hover:text-brand-300 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* TOPIC GRID */}
      <section>
        <div className="flex items-baseline justify-between mb-4">
          <h2 className="text-xl font-semibold tracking-tight">Tēmu kolekcijas</h2>
          <span className="text-xs text-slate-500">Pārlūko pēc tēmas</span>
        </div>
        {topics.length === 0 ? (
          loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="skeleton h-24 rounded-xl" />
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">Tēmas vēl nav ielasītas.</p>
          )
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {topics.map(({ topic, count }) => (
              <Link
                key={topic}
                to={`/tema/${topic}`}
                className="group relative rounded-xl border border-slate-200/70 dark:border-slate-800 bg-white/90 dark:bg-slate-900/70 p-4 shadow-soft hover:shadow-lift hover:border-brand-400 hover:-translate-y-0.5 transition-all duration-200"
              >
                <div className="text-2xl mb-2 transition-transform group-hover:scale-110">
                  {TOPIC_ICONS[topic] || '📑'}
                </div>
                <div className="font-semibold text-sm text-slate-900 dark:text-slate-100">
                  {TOPIC_LABELS[topic] || topic}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  {count} {count === 1 ? 'dokuments' : 'dokumenti'}
                </div>
                <span aria-hidden className="absolute top-3 right-3 text-slate-300 dark:text-slate-700 group-hover:text-brand-500 transition-colors">→</span>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* RECENT */}
      <section>
        <div className="flex items-baseline justify-between mb-4">
          <h2 className="text-xl font-semibold tracking-tight">Jaunākie ieraksti</h2>
          <Link
            to="/meklet"
            className="text-xs font-medium text-brand-600 dark:text-brand-400 hover:underline"
          >
            Skatīt visus →
          </Link>
        </div>
        {loading ? (
          <div className="grid md:grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : recent.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/50 p-8 text-center">
            <div className="text-3xl mb-2">📭</div>
            <p className="font-medium mb-2 text-slate-800 dark:text-slate-200">
              Datubāze ir tukša.
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Palaidiet{' '}
              <code className="font-mono text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                python seed_data.py
              </code>
              {' '}vai{' '}
              <code className="font-mono text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                python import_runner.py --source data_gov_lv
              </code>.
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {recent.map((doc) => <DocumentCard key={doc.id} doc={doc} />)}
          </div>
        )}
      </section>
    </div>
  )
}
