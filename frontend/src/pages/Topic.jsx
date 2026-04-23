import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api.js'
import Breadcrumb from '../components/Breadcrumb.jsx'
import DocumentCard from '../components/DocumentCard.jsx'
import { CardSkeleton } from '../components/PageSkeleton.jsx'
import { TOPIC_LABELS, TOPIC_ICONS } from '../labels.js'

export default function Topic() {
  const { topic } = useParams()
  const [results, setResults] = useState({ total: 0, items: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.listDocuments({ topic, limit: 100 })
      .then(setResults)
      .finally(() => setLoading(false))
  }, [topic])

  const label = TOPIC_LABELS[topic] || topic
  const icon = TOPIC_ICONS[topic] || '📑'

  return (
    <div className="animate-fade-in">
      <Breadcrumb items={[
        { label: 'Sākums', to: '/' },
        { label: 'Tēmas' },
        { label },
      ]} />

      {/* Tēmas virsraksta kartīte */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-200/70 dark:border-slate-800 bg-gradient-to-br from-white via-brand-50/30 to-white dark:from-slate-900 dark:via-brand-950/30 dark:to-slate-900 px-6 py-8 md:px-8 md:py-10 mb-6 shadow-soft">
        <div aria-hidden className="pointer-events-none absolute -top-16 -right-12 h-48 w-48 rounded-full bg-brand-300/25 dark:bg-brand-600/15 blur-3xl" />
        <div className="relative flex items-start gap-4">
          <div className="shrink-0 w-14 h-14 md:w-16 md:h-16 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center text-3xl md:text-4xl shadow-soft">
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-400 mb-1">
              Tēma
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">{label}</h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2 max-w-2xl">
              Dokumenti, kas saistīti ar tēmu "{label}". Klasifikācija ir heuristiska —
              autoritatīvo saturu skatīt oficiālajā avotā.
            </p>
          </div>
          {!loading && (
            <div className="hidden md:block shrink-0 text-right">
              <div className="text-3xl font-bold text-brand-600 dark:text-brand-400">
                {results.total}
              </div>
              <div className="text-xs text-slate-500 uppercase tracking-wide">
                dokumenti
              </div>
            </div>
          )}
        </div>
      </section>

      {loading ? (
        <div className="grid md:grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : (
        <>
          <div className="text-sm text-slate-500 mb-3 md:hidden">
            {results.total} dokumenti
          </div>
          {results.items.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/50 p-8 text-center">
              <div className="text-3xl mb-2">🗂️</div>
              <p className="text-slate-600 dark:text-slate-400">
                Šajā tēmā vēl nav dokumentu.
              </p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-3">
              {results.items.map((doc) => <DocumentCard key={doc.id} doc={doc} />)}
            </div>
          )}
        </>
      )}
    </div>
  )
}
