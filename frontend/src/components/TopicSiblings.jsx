import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  TOPIC_LABELS, TOPIC_ICONS, DOC_TYPE_LABELS, STATUS_LABELS, STATUS_COLORS,
} from '../labels.js'

/**
 * Atzarojums ar tās pašas kategorijas (tēmas) dokumentiem.
 *
 * Props:
 *  - groups: [{ topic, total, items: [{ id, doc_type, title, number, issuer, status }] }]
 *  - currentId: pašreizējā dokumenta ID (lai to izslēgtu, ja nejauši ielec)
 */
export default function TopicSiblings({ groups, currentId }) {
  if (!groups || groups.length === 0) return null

  return (
    <section className="mb-6">
      <h2 className="text-lg font-semibold mb-2">Šīs kategorijas dokumenti</h2>
      <p className="text-xs text-slate-500 mb-3">
        Citi dokumenti, kas pieder tām pašām tēmām. Dokumenti, kas atkārtojas vairākās
        tēmās, parādās tikai vienu reizi.
      </p>
      <div className="space-y-3">
        {groups.map((g) => (
          <TopicGroup key={g.topic} group={g} currentId={currentId} />
        ))}
      </div>
    </section>
  )
}

function TopicGroup({ group, currentId }) {
  const [open, setOpen] = useState(true)
  const icon = TOPIC_ICONS[group.topic] || '•'
  const label = TOPIC_LABELS[group.topic] || group.topic
  const items = (group.items || []).filter((d) => d.id !== currentId)
  const shown = items.length
  const hasMore = group.total > shown

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-3 px-3 py-2 text-left"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2 min-w-0">
          <span className="text-slate-400 text-xs w-3 text-center shrink-0">
            {open ? '▾' : '▸'}
          </span>
          <span className="text-base" aria-hidden>{icon}</span>
          <span className="font-medium truncate">{label}</span>
        </span>
        <span className="text-xs text-slate-500 shrink-0">
          {shown}{hasMore ? ` no ${group.total}` : ''}
        </span>
      </button>
      {open && (
        <ul className="border-t border-slate-100 dark:border-slate-800">
          {items.length === 0 ? (
            <li className="px-3 py-3 text-sm text-slate-500">
              Citu dokumentu nav.
            </li>
          ) : (
            items.map((d) => <SiblingRow key={d.id} doc={d} />)
          )}
          {hasMore && (
            <li className="px-3 py-2 border-t border-slate-100 dark:border-slate-800">
              <Link
                to={`/tema/${group.topic}`}
                className="text-sm text-brand-600 dark:text-brand-400 hover:underline"
              >
                Skatīt visus {group.total} dokumentus tēmā "{label}" →
              </Link>
            </li>
          )}
        </ul>
      )}
    </div>
  )
}

function SiblingRow({ doc }) {
  return (
    <li className="px-3 py-2 border-t border-slate-100 dark:border-slate-800 first:border-t-0">
      <div className="flex items-start gap-2 flex-wrap">
        <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 shrink-0 mt-0.5">
          {DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type}
        </span>
        <span
          className={`text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded shrink-0 mt-0.5 ${STATUS_COLORS[doc.status] || ''}`}
          title={STATUS_LABELS[doc.status] || doc.status}
        >
          {STATUS_LABELS[doc.status] || doc.status}
        </span>
        <Link
          to={`/dokuments/${doc.id}`}
          className="flex-1 min-w-0 text-sm text-slate-800 dark:text-slate-100 hover:text-brand-700 dark:hover:text-brand-400 hover:underline"
        >
          {doc.number && <span className="font-mono text-xs text-slate-500 mr-1">{doc.number}</span>}
          {doc.title}
          {doc.issuer && (
            <span className="block text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {doc.issuer}
            </span>
          )}
        </Link>
      </div>
    </li>
  )
}
