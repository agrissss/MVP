import { useEffect, useState, useMemo } from 'react'
import { api } from '../api.js'
import { SECTION_LEVEL_LABELS } from '../labels.js'

/**
 * Inline lasītājs likuma struktūrai — nodaļa → pants → daļa → punkts —
 * ar pilniem fragmentiem, lai lietotājam nav jāatver oficiālais avots.
 *
 * Atšķirībā no SectionTree (sānjoslas TOC), šis ir plūstošs lasāms izkārtojums:
 *  - Nodaļa ir liela virsraksta kartīte.
 *  - Pants — kartīte ar numuru, nosaukumu un ievada tekstu.
 *  - Daļas — iekšā atsevišķi paragrāfi ar numuru "(N)".
 *  - Punkti — sarakstā ar "1)", "2)".
 *
 * Props:
 *  - docId: dokumenta ID
 *  - officialUrl: bāzes oficiālais URL (katrs pants sasaista ar savu anchor)
 */
export default function SectionReader({ docId, officialUrl }) {
  const [sections, setSections] = useState(null)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')

  useEffect(() => {
    setSections(null)
    setError(null)
    api.getSections(docId)
      .then(setSections)
      .catch((e) => setError(e.message || String(e)))
  }, [docId])

  const qLower = query.trim().toLowerCase()
  const filtered = useMemo(() => {
    if (!sections) return []
    if (!qLower) return sections
    return filterTree(sections, qLower)
  }, [sections, qLower])

  if (error) {
    return (
      <div className="rounded-xl border border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-900/30 p-4 text-sm text-rose-800 dark:text-rose-200">
        <div className="font-semibold mb-1">Neizdevās ielādēt saturu</div>
        <div className="font-mono text-xs">{error}</div>
      </div>
    )
  }

  if (!sections) {
    return (
      <div className="rounded-xl border border-slate-200/70 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 animate-pulse">
        <div className="h-5 w-1/3 bg-slate-200 dark:bg-slate-800 rounded mb-4" />
        <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded mb-2" />
        <div className="h-3 w-5/6 bg-slate-100 dark:bg-slate-800 rounded mb-2" />
        <div className="h-3 w-4/6 bg-slate-100 dark:bg-slate-800 rounded" />
      </div>
    )
  }

  if (sections.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/50 p-8 text-center">
        <div className="text-3xl mb-2">📖</div>
        <p className="text-slate-600 dark:text-slate-400 mb-1 font-medium">
          Šim dokumentam vēl nav strukturētu pantu.
        </p>
        <p className="text-sm text-slate-500">
          Atveriet oficiālo avotu, lai lasītu pilnu tekstu.
        </p>
      </div>
    )
  }

  return (
    <section className="rounded-2xl border border-slate-200/70 dark:border-slate-800 bg-white/90 dark:bg-slate-900/70 shadow-soft overflow-hidden">
      {/* Galva */}
      <div className="flex items-center gap-3 flex-wrap px-4 md:px-6 py-4 border-b border-slate-200/70 dark:border-slate-800 bg-gradient-to-r from-brand-50/50 via-transparent to-transparent dark:from-brand-950/30">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-400">
            📖 Lasāmais skats
          </div>
          <h2 className="text-lg md:text-xl font-bold tracking-tight">Likuma saturs</h2>
        </div>
        <div className="ml-auto flex-1 min-w-[200px] max-w-sm">
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filtrēt pantā vai tekstā…"
            className="w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
          />
        </div>
      </div>

      {/* Saturs */}
      <div className="divide-y divide-slate-100 dark:divide-slate-800">
        {filtered.length === 0 ? (
          <div className="p-6 text-center text-sm text-slate-500">
            Nav atrasts neviens pants vai punkts, kas atbilst "{query}".
          </div>
        ) : (
          filtered.map((s) => (
            <NodeRenderer key={s.id} section={s} officialUrl={officialUrl} depth={0} />
          ))
        )}
      </div>

      {/* Kājene */}
      <div className="px-4 md:px-6 py-3 border-t border-slate-200/70 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 text-xs text-slate-500 flex flex-wrap gap-2 items-center">
        <span>
          Fragmenti ir ievada citāti (max ~280 rakstzīmes) ātrai orientācijai.
        </span>
        <a
          href={officialUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto text-brand-700 dark:text-brand-400 hover:underline font-medium"
        >
          Pilns teksts oficiālajā avotā ↗
        </a>
      </div>
    </section>
  )
}

/* --- Rekursīvs renderētājs --- */
function NodeRenderer({ section, officialUrl, depth }) {
  const level = section.level

  if (level === 'nodala' || level === 'sadala') {
    return <ChapterBlock section={section} officialUrl={officialUrl} />
  }
  if (level === 'pants') {
    return <ArticleBlock section={section} officialUrl={officialUrl} />
  }
  if (level === 'dala') {
    return <PartBlock section={section} officialUrl={officialUrl} depth={depth} />
  }
  // punkts / apakspunkts
  return <PointBlock section={section} officialUrl={officialUrl} depth={depth} />
}

/* Nodaļa — liela sadaļa ar panti iekšā.
   Nodaļas anchor (piem., "n4") uz likumi.lv bieži neeksistē —
   tāpēc saite uz oficiālo avotu izmanto pirmā panta (p{N}) anchor,
   kurš uz likumi.lv vienmēr ir pieejams. */
function ChapterBlock({ section, officialUrl }) {
  const firstArticle = findFirstArticle(section)
  const deepLink =
    (firstArticle && firstArticle.deep_link) ||
    (firstArticle && firstArticle.anchor
      ? officialUrl + '#' + firstArticle.anchor
      : null) ||
    section.deep_link ||
    (officialUrl + (section.anchor ? `#${section.anchor}` : ''))
  return (
    <div className="px-4 md:px-6 py-5 md:py-6 bg-gradient-to-b from-brand-50/30 to-transparent dark:from-brand-950/20">
      <div className="flex items-baseline gap-2 flex-wrap mb-1">
        <span className="text-[10px] uppercase tracking-wide font-bold text-brand-700 dark:text-brand-400 bg-brand-100 dark:bg-brand-900/40 px-2 py-0.5 rounded-full">
          {SECTION_LEVEL_LABELS[section.level] || section.level} {section.number}
        </span>
        <a
          href={deepLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-400 hover:text-brand-600 text-xs"
          title="Atvērt nodaļu oficiālajā avotā"
        >
          ↗
        </a>
      </div>
      <h3 className="text-lg md:text-xl font-bold text-slate-900 dark:text-slate-50 mb-3">
        {section.title || `Nodaļa ${section.number}`}
      </h3>
      {section.children && section.children.length > 0 && (
        <div className="space-y-3 mt-4">
          {section.children.map((c) => (
            <NodeRenderer key={c.id} section={c} officialUrl={officialUrl} depth={1} />
          ))}
        </div>
      )}
    </div>
  )
}

/* Pants — karte ar virsrakstu, ievada tekstu un daļām */
function ArticleBlock({ section, officialUrl }) {
  const deepLink = section.deep_link || (officialUrl + (section.anchor ? `#${section.anchor}` : ''))
  return (
    <article
      id={`p${section.number}`}
      className="scroll-mt-24 rounded-xl border border-slate-200/70 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 md:px-5 py-4 hover:border-brand-300 dark:hover:border-brand-700 transition-colors"
    >
      <div className="flex items-baseline gap-2 flex-wrap mb-1.5">
        <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-800 dark:text-amber-300 bg-amber-100 dark:bg-amber-900/40 px-2 py-0.5 rounded border border-amber-200 dark:border-amber-800">
          {section.number}. pants
        </span>
        {section.title && (
          <h4 className="text-base md:text-lg font-semibold text-slate-900 dark:text-slate-100">
            {section.title}
          </h4>
        )}
        <a
          href={deepLink}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto text-[11px] text-slate-400 hover:text-brand-600 dark:hover:text-brand-400"
          title="Atvērt pantu oficiālajā avotā"
        >
          ↗ likumi.lv
        </a>
      </div>
      {section.snippet && (
        <p className="text-sm md:text-[15px] leading-relaxed text-slate-700 dark:text-slate-300 mb-2">
          {section.snippet}
        </p>
      )}
      {section.children && section.children.length > 0 && (
        <div className="mt-3 space-y-2 pl-3 border-l-2 border-emerald-200 dark:border-emerald-800/60">
          {section.children.map((c) => (
            <NodeRenderer key={c.id} section={c} officialUrl={officialUrl} depth={2} />
          ))}
        </div>
      )}
    </article>
  )
}

/* Daļa — iekšēja apakšvienība pantā */
function PartBlock({ section, officialUrl, depth }) {
  return (
    <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
      <span className="font-semibold text-emerald-800 dark:text-emerald-300 mr-1.5">
        ({section.number})
      </span>
      {section.title && (
        <span className="font-medium text-slate-800 dark:text-slate-200">{section.title}. </span>
      )}
      {section.snippet && <span>{section.snippet}</span>}
      {section.children && section.children.length > 0 && (
        <ul className="mt-1.5 ml-5 space-y-1 list-none">
          {section.children.map((c) => (
            <NodeRenderer key={c.id} section={c} officialUrl={officialUrl} depth={depth + 1} />
          ))}
        </ul>
      )}
    </div>
  )
}

/* Punkts — uzskaitījumā */
function PointBlock({ section }) {
  return (
    <li className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed flex gap-2">
      <span className="font-semibold text-slate-500 dark:text-slate-500 shrink-0">
        {section.number})
      </span>
      <span>
        {section.title && <span className="font-medium">{section.title}. </span>}
        {section.snippet}
      </span>
    </li>
  )
}

/* --- Filtrēšana — saglabā vecākus, ja bērns atbilst --- */
function filterTree(nodes, q) {
  const result = []
  for (const n of nodes) {
    const self = matches(n, q)
    const kids = n.children ? filterTree(n.children, q) : []
    if (self || kids.length > 0) {
      result.push({ ...n, children: kids })
    }
  }
  return result
}

function matches(n, q) {
  const hay = [n.number, n.path, n.title, n.snippet].filter(Boolean).join(' ').toLowerCase()
  return hay.includes(q)
}

/* Atrod pirmo pants-līmeņa pēcteci (lai nodaļas saite ved uz reālu anchor).
   Likumi.lv nodaļu anchors (piem., "#n4") bieži neeksistē, toties
   pantu anchors ("#p{N}") vienmēr ir pieejami. Tāpēc nodaļas saite
   uz oficiālo avotu izmanto tās pirmā panta anchor — tas lietotāju
   aizved tieši uz nodaļas sākumu likumi.lv lapā. */
function findFirstArticle(section) {
  if (!section || !section.children) return null
  for (const c of section.children) {
    if (c.level === 'pants') return c
    const deep = findFirstArticle(c)
    if (deep) return deep
  }
  return null
}
