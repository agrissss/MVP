import { useEffect, useState, useMemo } from 'react'
import { api } from '../api.js'
import { formatSectionLabel, SECTION_LEVEL_LABELS } from '../labels.js'

/**
 * Hierarhisks saturs (TOC) ar izvēršamiem zariem un deep-link uz oficiālo avotu.
 *
 * Galvenā doma: ātri un viegli sekot likuma struktūrai — nodaļa → pants → daļa.
 * Nodaļas un panti pēc noklusējuma izvērsti, daļas/punkti — sakļauti.
 *
 * Props:
 *  - docId: dokumenta ID, par kuru ielādēt sekcijas
 *  - officialUrl: bāzes oficiālā avota URL (ja deep_link nav komplektā)
 *  - compact: true → sānjoslas variants (mazāks padding, mazāks fonts)
 */
export default function SectionTree({ docId, officialUrl, compact = false }) {
  const [sections, setSections] = useState(null)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [expandAll, setExpandAll] = useState(null) // null = noklusējums, true/false = force

  useEffect(() => {
    api.getSections(docId)
      .then(setSections)
      .catch((e) => setError(e.message || String(e)))
  }, [docId])

  // Skaitām sekcijas pa līmeņiem priekš kopsavilkuma
  const counts = useMemo(() => countByLevel(sections || []), [sections])

  if (error) {
    const looksLikeNetwork = /fetch|network|failed|load/i.test(error)
    return (
      <div className="rounded-lg border border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-900/30 p-3 text-sm text-rose-800 dark:text-rose-200">
        <div className="font-semibold mb-1">Neizdevās ielādēt saturu</div>
        <div className="font-mono text-xs mb-2">{error}</div>
        {looksLikeNetwork && (
          <div className="text-xs">
            Backend nav sasniedzams. Pārbaudi, vai <code className="font-mono">uvicorn app.main:app --reload</code> darbojas.
          </div>
        )}
      </div>
    )
  }
  if (!sections) return <p className="text-sm text-slate-500">Ielādē saturu…</p>
  if (sections.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Šim dokumentam vēl nav strukturētu pantu/punktu. Atveriet oficiālo avotu, lai lasītu pilnu tekstu.
      </p>
    )
  }

  const qLower = query.trim().toLowerCase()
  const match = (s) => {
    if (!qLower) return true
    const hay = [s.number, s.path, s.title, s.snippet].filter(Boolean).join(' ').toLowerCase()
    return hay.includes(qLower)
  }

  // Ja lietotājs meklē, automātiski paplašinām visu, lai redzētu trāpījumus
  const effectiveExpand = qLower ? true : expandAll

  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={compact ? 'Filtrēt…' : 'Filtrēt pantu/punktu (piem., 46 vai pārbaudes)'}
          className="flex-1 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-1.5 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="text-xs text-slate-500 hover:text-slate-700"
            title="Notīrīt filtru"
          >
            ✕
          </button>
        )}
      </div>

      {!compact && (
        <div className="flex items-center justify-between mb-3 text-[11px]">
          <div className="flex flex-wrap gap-1.5 text-slate-500">
            {counts.nodala > 0 && <LevelPill level="nodala" count={counts.nodala} />}
            {counts.pants > 0 && <LevelPill level="pants" count={counts.pants} />}
            {counts.dala > 0 && <LevelPill level="dala" count={counts.dala} />}
            {counts.punkts > 0 && <LevelPill level="punkts" count={counts.punkts} />}
          </div>
          <div className="flex gap-1 shrink-0">
            <button
              onClick={() => setExpandAll(true)}
              className="px-2 py-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
            >
              Izvērst visu
            </button>
            <button
              onClick={() => setExpandAll(false)}
              className="px-2 py-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
            >
              Sakļaut
            </button>
          </div>
        </div>
      )}

      <ul className={compact ? 'text-[13px] space-y-0.5' : 'text-sm space-y-0.5'}>
        {sections.map((s) => (
          <SectionNode
            key={s.id}
            section={s}
            match={match}
            officialUrl={officialUrl}
            depth={0}
            compact={compact}
            forceExpand={effectiveExpand}
          />
        ))}
      </ul>

      {!compact && (
        <p className="text-xs text-slate-500 mt-3">
          Fragmenti ir ievada citāti (max ~280 rakstzīmes) meklēšanai.
          Autoritatīvais teksts atrodas oficiālajā avotā.
        </p>
      )}
    </div>
  )
}

/* --- Līmeņu konfigurācija --- */
const LEVEL_STYLES = {
  sadala:      { bg: 'bg-violet-100 dark:bg-violet-900/40', text: 'text-violet-800 dark:text-violet-300', ring: 'border-violet-300 dark:border-violet-800' },
  nodala:      { bg: 'bg-brand-100  dark:bg-brand-900/40',  text: 'text-brand-800  dark:text-brand-300',  ring: 'border-brand-300  dark:border-brand-800' },
  pants:       { bg: 'bg-amber-100  dark:bg-amber-900/40',  text: 'text-amber-800  dark:text-amber-300',  ring: 'border-amber-300  dark:border-amber-800' },
  dala:        { bg: 'bg-emerald-100 dark:bg-emerald-900/40', text: 'text-emerald-800 dark:text-emerald-300', ring: 'border-emerald-300 dark:border-emerald-800' },
  punkts:      { bg: 'bg-slate-100  dark:bg-slate-800',     text: 'text-slate-700  dark:text-slate-300',  ring: 'border-slate-300  dark:border-slate-700' },
  apakspunkts: { bg: 'bg-slate-100  dark:bg-slate-800',     text: 'text-slate-600  dark:text-slate-400',  ring: 'border-slate-300  dark:border-slate-700' },
}

function levelStyle(level) {
  return LEVEL_STYLES[level] || LEVEL_STYLES.punkts
}

function LevelPill({ level, count }) {
  const s = levelStyle(level)
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full ${s.bg} ${s.text} font-semibold`}>
      {SECTION_LEVEL_LABELS[level] || level}: {count}
    </span>
  )
}

/* --- Rekursīvs koka mezgls --- */
function SectionNode({ section, match, officialUrl, depth, compact, forceExpand }) {
  const hasChildren = section.children && section.children.length > 0
  // Noklusējums: nodaļas un panti izvērsti; daļas/punkti sakļauti
  const defaultOpen = section.level === 'nodala' || section.level === 'pants'
  const [openLocal, setOpenLocal] = useState(defaultOpen)
  const open = forceExpand === null ? openLocal : forceExpand

  const selfMatch = match(section)
  const childMatches = hasChildren && section.children.some((c) => containsMatch(c, match))
  if (!selfMatch && !childMatches) return null

  const deepLink = section.deep_link || (officialUrl + (section.anchor ? `#${section.anchor}` : ''))
  const style = levelStyle(section.level)
  const levelLabel = SECTION_LEVEL_LABELS[section.level] || section.level

  // Indent un border-l krāsa atkarīga no līmeņa
  const padY = compact ? 'py-0.5' : 'py-1'
  const indent = depth * (compact ? 10 : 14)

  const isStructural = section.level === 'nodala' || section.level === 'sadala'
  const numberFontWeight = isStructural ? 'font-bold' : 'font-semibold'

  return (
    <li
      className={`relative border-l-2 ${style.ring} ${padY} pl-2`}
      style={{ marginLeft: indent }}
    >
      <div className="flex items-start gap-1.5">
        {hasChildren ? (
          <button
            onClick={() => { setOpenLocal(!open) }}
            className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 mt-0.5 w-4 text-center shrink-0"
            aria-label={open ? 'Sakļaut' : 'Izvērst'}
          >
            {open ? '▾' : '▸'}
          </button>
        ) : (
          <span className="w-4 shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`text-[9px] uppercase tracking-wide ${style.text} ${style.bg} px-1.5 py-0.5 rounded font-semibold shrink-0`}>
              {levelLabel}
            </span>
            <a
              href={deepLink}
              target="_blank"
              rel="noopener noreferrer"
              className={`${numberFontWeight} ${isStructural ? 'text-slate-900 dark:text-slate-50' : 'text-brand-700 dark:text-brand-400'} hover:underline truncate`}
              title={`${formatSectionLabel(section)}${section.title ? ' — ' + section.title : ''} (atvērt likumi.lv)`}
            >
              {formatSectionLabel(section)}
            </a>
            {section.title && !compact && (
              <span className={`${isStructural ? 'text-slate-800 dark:text-slate-200 font-medium' : 'text-slate-700 dark:text-slate-300'}`}>
                — {section.title}
              </span>
            )}
            {hasChildren && !compact && (
              <span className="text-[10px] text-slate-400 ml-auto shrink-0">
                {section.children.length}
              </span>
            )}
          </div>
          {section.title && compact && (
            <div className="text-slate-600 dark:text-slate-400 text-[12px] truncate" title={section.title}>
              {section.title}
            </div>
          )}
          {section.snippet && !compact && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
              {section.snippet}
            </p>
          )}
        </div>
      </div>
      {hasChildren && open && (
        <ul className="mt-0.5 space-y-0.5">
          {section.children.map((c) => (
            <SectionNode
              key={c.id}
              section={c}
              match={match}
              officialUrl={officialUrl}
              depth={depth + 1}
              compact={compact}
              forceExpand={forceExpand}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

function containsMatch(section, match) {
  if (match(section)) return true
  if (!section.children) return false
  return section.children.some((c) => containsMatch(c, match))
}

function countByLevel(sections) {
  const acc = { sadala: 0, nodala: 0, pants: 0, dala: 0, punkts: 0, apakspunkts: 0 }
  const walk = (arr) => {
    for (const s of arr) {
      if (acc[s.level] !== undefined) acc[s.level]++
      if (s.children && s.children.length) walk(s.children)
    }
  }
  walk(sections)
  return acc
}
