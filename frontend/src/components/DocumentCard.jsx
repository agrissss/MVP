import { Link } from 'react-router-dom'
import { api } from '../api.js'
import {
  DOC_TYPE_LABELS, STATUS_LABELS, STATUS_COLORS, SOURCE_LABELS, TOPIC_LABELS,
  formatDate,
} from '../labels.js'

export default function DocumentCard({ doc }) {
  // Hover prefetch — ieslēdz pilnu dokumenta ielādi klusumā, lai klikšķis ir instant
  const handlePrefetch = () => { api.prefetchDocument(doc.id).catch(() => {}) }

  return (
    <article
      className="group rounded-xl border border-slate-200/70 dark:border-slate-800/70 bg-white/90 dark:bg-slate-900/70 p-4 shadow-soft hover:shadow-lift hover:border-brand-300 dark:hover:border-brand-700 transition-all duration-200"
      onMouseEnter={handlePrefetch}
      onFocus={handlePrefetch}
    >
      <div className="flex items-start justify-between gap-3 mb-2 flex-wrap">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            {DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type}
          </span>
          <span className={`text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded ${STATUS_COLORS[doc.status] || ''}`}>
            {STATUS_LABELS[doc.status] || doc.status}
          </span>
          {doc.number && (
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              {doc.number}
            </span>
          )}
        </div>
        <span className="text-[11px] text-slate-500 dark:text-slate-400">
          {SOURCE_LABELS[doc.source] || doc.source}
        </span>
      </div>

      <h3 className="text-[15px] font-semibold leading-snug mb-1">
        <Link
          to={`/dokuments/${doc.id}`}
          className="text-slate-900 dark:text-slate-100 group-hover:text-brand-700 dark:group-hover:text-brand-400 transition-colors"
        >
          {doc.title}
        </Link>
      </h3>

      {doc.issuer && (
        <p className="text-sm text-slate-600 dark:text-slate-400">{doc.issuer}</p>
      )}

      {doc.summary && (
        <p className="text-sm mt-2 text-slate-700 dark:text-slate-300 line-clamp-2">
          {doc.summary}
        </p>
      )}

      <div className="flex items-center gap-2 mt-3 text-[11px] text-slate-500 dark:text-slate-400 flex-wrap">
        {doc.adopted_date && <span>Pieņemts · {formatDate(doc.adopted_date)}</span>}
        {doc.effective_date && <span>· Spēkā no {formatDate(doc.effective_date)}</span>}
        {doc.topics && doc.topics.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {doc.topics.slice(0, 3).map((t) => (
              <span
                key={t}
                className="px-1.5 py-0.5 rounded-full bg-brand-50 dark:bg-brand-950/40 text-brand-700 dark:text-brand-300 text-[10px] font-medium"
              >
                {TOPIC_LABELS[t] || t}
              </span>
            ))}
            {doc.topics.length > 3 && (
              <span className="text-[10px] text-slate-400">+{doc.topics.length - 3}</span>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 flex gap-2 flex-wrap">
        <Link
          to={`/dokuments/${doc.id}`}
          className="text-sm px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors"
        >
          Skatīt kartīti
        </Link>
        <a
          href={doc.official_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white shadow-soft transition-all"
        >
          Oficiālais avots ↗
        </a>
      </div>
    </article>
  )
}
