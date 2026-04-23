import { useEffect, useState } from 'react'
import { api } from '../api.js'
import Breadcrumb from '../components/Breadcrumb.jsx'
import { CardSkeleton } from '../components/PageSkeleton.jsx'
import { formatDateTime } from '../labels.js'

const SOURCE_ICONS = {
  likumi_lv: '⚖️',
  data_gov_lv: '📊',
  vid: '💶',
  atd: '🚚',
}

export default function Sources() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.listSources().then(setSources).finally(() => setLoading(false))
  }, [])

  return (
    <div className="animate-fade-in">
      <Breadcrumb items={[{ label: 'Sākums', to: '/' }, { label: 'Avoti' }]} />
      <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">Oficiālie avoti</h1>
      <p className="text-slate-600 dark:text-slate-400 mb-6 max-w-2xl">
        Sistēma izmanto tikai oficiālus publiskus avotus. Šeit redzams to saraksts
        ar pēdējā importa statusu un licences informāciju.
      </p>

      {loading ? (
        <div className="grid md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : sources.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/50 p-8 text-center">
          <p className="text-slate-600 dark:text-slate-400">Avoti vēl nav ielasīti.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {sources.map((s) => (
            <article
              key={s.code}
              className="group rounded-xl border border-slate-200/70 dark:border-slate-800 bg-white/90 dark:bg-slate-900/70 p-5 shadow-soft hover:shadow-lift hover:border-brand-300 transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="shrink-0 w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center text-xl">
                  {SOURCE_ICONS[s.code] || '📄'}
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                    {s.name}
                  </h2>
                  <a
                    href={s.base_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-brand-600 dark:text-brand-400 hover:underline break-all block mt-0.5"
                  >
                    {s.base_url} ↗
                  </a>
                </div>
              </div>

              {s.license_notes && (
                <p className="text-sm text-slate-700 dark:text-slate-300 mt-3 leading-relaxed">
                  {s.license_notes}
                </p>
              )}

              <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
                <MetaRow
                  label="Pēdējais imports"
                  value={formatDateTime(s.last_import_at)}
                />
                <MetaRow
                  label="Ierakstu skaits"
                  value={s.last_import_count ?? '—'}
                />
                <div className="col-span-2 flex items-center gap-2">
                  <dt className="text-slate-500 dark:text-slate-400">Statuss:</dt>
                  <dd><StatusBadge status={s.last_import_status} /></dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

function MetaRow({ label, value }) {
  return (
    <div>
      <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className="font-medium text-slate-800 dark:text-slate-200 mt-0.5">
        {value}
      </dd>
    </div>
  )
}

function StatusBadge({ status }) {
  const styles = {
    ok: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
    failed: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 border-rose-200 dark:border-rose-800',
    partial: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-800',
  }
  const cls = styles[status] ||
    'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600'
  const labels = { ok: 'veiksmīgs', failed: 'neizdevās', partial: 'daļējs' }
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${cls}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-70" />
      {labels[status] || status || '—'}
    </span>
  )
}
