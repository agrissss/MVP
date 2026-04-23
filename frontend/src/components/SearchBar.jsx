import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import {
  DOC_TYPE_LABELS, SECTION_LEVEL_LABELS, TOPIC_LABELS, TOPIC_ICONS,
  formatSectionLabel,
} from '../labels.js'

/**
 * Meklēšanas lauks ar reallaika ieteikumu dropdown.
 *
 * Props:
 *  - value: sākotnējais teksts (no URL ?q=)
 *  - onSubmit: tiek izsaukts ar final tekstu, kad lietotājs nospiež Enter vai klikšķina "Meklēt"
 *  - placeholder
 */
export default function SearchBar({
  value,
  onSubmit,
  placeholder = 'Meklēt likumus, MK noteikumus, datu kopas…',
}) {
  const [text, setText] = useState(value || '')
  const [suggestions, setSuggestions] = useState(null) // {documents, sections, topics} vai null
  const [open, setOpen] = useState(false)
  const [hi, setHi] = useState(-1) // highlighted index visā plakanajā sarakstā
  const [loading, setLoading] = useState(false)
  const abortRef = useRef(null)
  const wrapRef = useRef(null)
  const navigate = useNavigate()

  // sinhronizē ārējo value (piem., pēc URL izmaiņām)
  useEffect(() => { setText(value || '') }, [value])

  // Debounced suggest zvans
  useEffect(() => {
    const q = text.trim()
    if (q.length < 2) {
      setSuggestions(null)
      setLoading(false)
      return
    }
    const handle = setTimeout(() => {
      if (abortRef.current) abortRef.current.abort()
      const ctrl = new AbortController()
      abortRef.current = ctrl
      setLoading(true)
      api.suggest(q, ctrl.signal)
        .then((res) => {
          setSuggestions(res)
          setHi(-1)
          setLoading(false)
        })
        .catch((e) => {
          if (e.name === 'AbortError') return
          setSuggestions(null)
          setLoading(false)
        })
    }, 150)
    return () => clearTimeout(handle)
  }, [text])

  // Klikšķis ārpus dropdown — aizver
  useEffect(() => {
    const onDocClick = (e) => {
      if (!wrapRef.current) return
      if (!wrapRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  // Plakans saraksts navigācijai ↑/↓
  const flat = []
  if (suggestions) {
    for (const d of suggestions.documents) flat.push({ kind: 'document', item: d })
    for (const s of suggestions.sections) flat.push({ kind: 'section', item: s })
    for (const t of suggestions.topics) flat.push({ kind: 'topic', item: t })
  }
  const showDropdown = open && text.trim().length >= 2 &&
    (loading || (suggestions && (flat.length > 0 || text.trim().length >= 2)))

  const navigateTo = (entry) => {
    setOpen(false)
    if (!entry) return
    if (entry.kind === 'document') navigate(`/dokuments/${entry.item.id}`)
    else if (entry.kind === 'section') navigate(`/dokuments/${entry.item.document_id}`)
    else if (entry.kind === 'topic') navigate(`/tema/${entry.item.topic}`)
  }

  const submit = (q) => {
    setOpen(false)
    onSubmit(q.trim())
  }

  const onKey = (e) => {
    if (!showDropdown || flat.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault()
        submit(text)
      }
      return
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setHi((h) => (h + 1) % flat.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setHi((h) => (h - 1 + flat.length) % flat.length)
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (hi >= 0 && hi < flat.length) navigateTo(flat[hi])
      else submit(text)
    } else if (e.key === 'Escape') {
      setOpen(false)
    }
  }

  return (
    <div ref={wrapRef} className="relative">
      <form
        onSubmit={(e) => { e.preventDefault(); submit(text) }}
        className="flex gap-2"
      >
        <input
          type="search"
          value={text}
          onChange={(e) => { setText(e.target.value); setOpen(true) }}
          onFocus={() => setOpen(true)}
          onKeyDown={onKey}
          placeholder={placeholder}
          className="flex-1 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
          aria-label="Meklēšanas vaicājums"
          autoComplete="off"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-md bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium"
        >
          Meklēt
        </button>
      </form>

      {showDropdown && (
        <div className="absolute left-0 right-0 mt-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg z-20 max-h-[70vh] overflow-y-auto">
          {loading && !suggestions && (
            <div className="px-3 py-2 text-xs text-slate-500">Meklē…</div>
          )}
          {suggestions && flat.length === 0 && !loading && (
            <div className="px-3 py-2 text-xs text-slate-500">
              Nav ieteikumu. Spied <kbd>Enter</kbd>, lai veiktu pilnu meklēšanu.
            </div>
          )}
          {renderGroup(
            'Dokumenti',
            suggestions?.documents || [],
            flat,
            hi,
            (d, idx) => (
              <DocRow key={`d-${d.id}`} doc={d} active={hi === idx}
                onClick={() => navigateTo({ kind: 'document', item: d })}
                onMouseEnter={() => setHi(idx)} />
            ),
            'document',
          )}
          {renderGroup(
            'Panti / punkti',
            suggestions?.sections || [],
            flat,
            hi,
            (s, idx) => (
              <SectionRow key={`s-${s.id}`} sec={s} active={hi === idx}
                onClick={() => navigateTo({ kind: 'section', item: s })}
                onMouseEnter={() => setHi(idx)} />
            ),
            'section',
          )}
          {renderGroup(
            'Tēmas',
            suggestions?.topics || [],
            flat,
            hi,
            (t, idx) => (
              <TopicRow key={`t-${t.topic}`} topic={t} active={hi === idx}
                onClick={() => navigateTo({ kind: 'topic', item: t })}
                onMouseEnter={() => setHi(idx)} />
            ),
            'topic',
          )}
          <div className="border-t border-slate-200 dark:border-slate-800 px-3 py-1.5 text-[11px] text-slate-500">
            <kbd className="font-mono">↑</kbd>/<kbd className="font-mono">↓</kbd> navigācija ·
            <kbd className="font-mono ml-1">Enter</kbd> atvērt ·
            <kbd className="font-mono ml-1">Esc</kbd> aizvērt
          </div>
        </div>
      )}
    </div>
  )
}

function renderGroup(title, items, flat, hi, renderer, kind) {
  if (items.length === 0) return null
  const offset = flat.findIndex((e) => e.kind === kind)
  return (
    <div className="py-1">
      <div className="px-3 pt-1 pb-1 text-[10px] uppercase tracking-wide font-semibold text-slate-500">
        {title}
      </div>
      {items.map((it, i) => renderer(it, offset + i))}
    </div>
  )
}

function DocRow({ doc, active, onClick, onMouseEnter }) {
  return (
    <button
      type="button"
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      className={
        'w-full text-left px-3 py-1.5 flex items-start gap-2 ' +
        (active ? 'bg-brand-50 dark:bg-brand-900/30' : 'hover:bg-slate-50 dark:hover:bg-slate-800')
      }
    >
      <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 shrink-0 mt-0.5">
        {DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type}
      </span>
      <span className="flex-1 min-w-0">
        <span className="text-sm block truncate">
          {doc.number && <span className="font-mono text-xs text-slate-500 mr-1">{doc.number}</span>}
          {doc.title}
        </span>
        {doc.issuer && (
          <span className="text-[11px] text-slate-500 block truncate">{doc.issuer}</span>
        )}
      </span>
    </button>
  )
}

function SectionRow({ sec, active, onClick, onMouseEnter }) {
  return (
    <button
      type="button"
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      className={
        'w-full text-left px-3 py-1.5 flex items-start gap-2 ' +
        (active ? 'bg-brand-50 dark:bg-brand-900/30' : 'hover:bg-slate-50 dark:hover:bg-slate-800')
      }
    >
      <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 shrink-0 mt-0.5">
        {SECTION_LEVEL_LABELS[sec.level] || sec.level}
      </span>
      <span className="flex-1 min-w-0">
        <span className="text-sm block truncate">
          <span className="font-medium">{formatSectionLabel(sec)}</span>
          {sec.title && <span className="text-slate-700 dark:text-slate-300"> — {sec.title}</span>}
        </span>
        <span className="text-[11px] text-slate-500 block truncate">
          {sec.document_title}
        </span>
        {sec.snippet && (
          <span className="text-[11px] text-slate-400 block truncate">
            {sec.snippet}
          </span>
        )}
      </span>
    </button>
  )
}

function TopicRow({ topic, active, onClick, onMouseEnter }) {
  return (
    <button
      type="button"
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      className={
        'w-full text-left px-3 py-1.5 flex items-center gap-2 ' +
        (active ? 'bg-brand-50 dark:bg-brand-900/30' : 'hover:bg-slate-50 dark:hover:bg-slate-800')
      }
    >
      <span className="text-base" aria-hidden>{TOPIC_ICONS[topic.topic] || '•'}</span>
      <span className="flex-1 text-sm truncate">
        {TOPIC_LABELS[topic.topic] || topic.topic}
      </span>
      <span className="text-[11px] text-slate-500 shrink-0">
        {topic.doc_count} dok.
      </span>
    </button>
  )
}
