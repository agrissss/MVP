import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api.js'
import Breadcrumb from '../components/Breadcrumb.jsx'
import SectionTree from '../components/SectionTree.jsx'
import SectionReader from '../components/SectionReader.jsx'
import TopicSiblings from '../components/TopicSiblings.jsx'
import {
  DOC_TYPE_LABELS, STATUS_LABELS, STATUS_COLORS,
  SOURCE_LABELS, TOPIC_LABELS, RELATION_LABELS,
  formatDate, formatDateTime,
} from '../labels.js'

export default function DocumentDetail() {
  const { id } = useParams()
  const [doc, setDoc] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setDoc(null)
    setError(null)
    api.getDocument(id).then(setDoc).catch((e) => setError(e.message || String(e)))
  }, [id])

  if (error) return <div className="text-rose-600">Kļūda: {error}</div>
  if (!doc) return <div>Ielādē…</div>

  const hasSections = doc.section_count > 0

  return (
    <div>
      <Breadcrumb items={[
        { label: 'Sākums', to: '/' },
        { label: 'Meklēšana', to: '/meklet' },
        { label: doc.title.length > 40 ? doc.title.slice(0, 40) + '…' : doc.title },
      ]} />

      <div className={hasSections ? 'grid lg:grid-cols-[1fr_340px] gap-6' : ''}>
        <article>
          <div className="flex items-center gap-2 flex-wrap mb-2">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700">
              {DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type}
            </span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${STATUS_COLORS[doc.status] || ''}`}>
              {STATUS_LABELS[doc.status] || doc.status}
            </span>
            {doc.number && (
              <span className="text-xs text-slate-500 dark:text-slate-400">{doc.number}</span>
            )}
            <span className="text-xs text-slate-500 dark:text-slate-400">
              Avots: {SOURCE_LABELS[doc.source] || doc.source}
            </span>
          </div>

          <h1 className="text-2xl font-bold mb-2">{doc.title}</h1>

          {doc.issuer && (
            <p className="text-slate-600 dark:text-slate-400 mb-4">{doc.issuer}</p>
          )}

          <a
            href={doc.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mb-6 px-4 py-2 rounded-md bg-brand-600 hover:bg-brand-700 text-white font-medium"
          >
            Atvērt oficiālo avotu ↗
          </a>

          {doc.summary && (
            <section className="mb-6">
              <h2 className="text-lg font-semibold mb-1">Īss apraksts</h2>
              <p className="text-slate-700 dark:text-slate-300">{doc.summary}</p>
              <p className="text-xs text-slate-500 mt-1">
                Apraksts nāk tieši no oficiālā avota metadatiem.
              </p>
            </section>
          )}

          {/* INLINE SATURA LASĪTĀJS — rāda pantus un to fragmentus tieši šeit,
              lai lietotājam nav jāatver oficiālais avots katru reizi. */}
          {hasSections && (
            <section className="mb-6">
              <SectionReader docId={doc.id} officialUrl={doc.official_url} />
            </section>
          )}

          <section className="mb-6 grid md:grid-cols-2 gap-4">
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-4">
              <h3 className="text-sm font-semibold mb-2">Metadati</h3>
              <dl className="text-sm space-y-1">
                <Row label="Pieņemts" value={formatDate(doc.adopted_date)} />
                <Row label="Spēkā no" value={formatDate(doc.effective_date)} />
                <Row label="Licence" value={doc.license || '—'} />
                <Row label="Iekšējais ID" value={doc.external_id} mono />
              </dl>
            </div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-4">
              <h3 className="text-sm font-semibold mb-2">Audits</h3>
              <dl className="text-sm space-y-1">
                <Row label="Pēdējais imports" value={formatDateTime(doc.last_imported)} />
                <Row label="Avots" value={SOURCE_LABELS[doc.source] || doc.source} />
              </dl>
              <p className="text-xs text-slate-500 mt-2">
                Autoritatīvo saturu skatīt oficiālajā avotā.
              </p>
            </div>
          </section>

          {doc.topics && doc.topics.length > 0 && (
            <section className="mb-6">
              <h2 className="text-lg font-semibold mb-2">Tēmas</h2>
              <div className="flex gap-2 flex-wrap">
                {doc.topics.map(t => (
                  <Link
                    key={t}
                    to={`/tema/${t}`}
                    className="px-2 py-1 rounded bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-400 text-sm"
                  >
                    {TOPIC_LABELS[t] || t}
                  </Link>
                ))}
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Tēmas tiek ieteiktas heuristiski — nav oficiāla klasifikācija.
              </p>
            </section>
          )}

          <TopicSiblings groups={doc.topic_siblings} currentId={doc.id} />

          {doc.related && doc.related.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Saistītie dokumenti</h2>
              <ul className="space-y-2">
                {doc.related.map((rel, i) => (
                  <li key={i} className="rounded border border-slate-200 dark:border-slate-800 p-3">
                    <div className="text-xs text-slate-500 mb-1">
                      {RELATION_LABELS[rel.relation_type] || rel.relation_type}
                    </div>
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                      <Link
                        to={`/dokuments/${rel.id}`}
                        className="font-medium hover:text-brand-600 dark:hover:text-brand-500"
                      >
                        [{DOC_TYPE_LABELS[rel.doc_type] || rel.doc_type}] {rel.title}
                      </Link>
                      <a
                        href={rel.official_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-brand-600 dark:text-brand-500 hover:underline"
                      >
                        Oficiālais avots ↗
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </article>

        {hasSections && (
          <aside className="hidden lg:block">
            <div className="sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
              <div className="flex items-baseline justify-between mb-3 gap-2">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">
                  Saturs
                </h2>
                <span className="text-xs text-slate-500">
                  {doc.section_count} ieraksti
                </span>
              </div>
              <SectionTree docId={doc.id} officialUrl={doc.official_url} compact />
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}

function Row({ label, value, mono }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className={mono ? 'font-mono text-xs text-right' : 'text-right'}>{value}</dd>
    </div>
  )
}
