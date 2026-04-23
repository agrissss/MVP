import { DOC_TYPE_LABELS, STATUS_LABELS, SOURCE_LABELS, TOPIC_LABELS } from '../labels.js'

/**
 * Sāna filtru panelis. Vizuāli saskaņots ar pārējo modernizēto dizainu —
 * rounded-xl kartīte, mīksta ēna, slim labels.
 */
export default function Filters({ value, onChange, topics = [] }) {
  const update = (k, v) => onChange({ ...value, [k]: v || undefined })

  const activeCount = Object.entries(value).filter(
    ([k, v]) => v && !['q', 'mode', 'limit', 'offset'].includes(k)
  ).length

  return (
    <aside className="rounded-xl border border-slate-200/70 dark:border-slate-800 bg-white/90 dark:bg-slate-900/70 p-4 shadow-soft space-y-4 lg:sticky lg:top-4 self-start">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Filtri
        </h3>
        {activeCount > 0 && (
          <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-brand-600/10 dark:bg-brand-500/20 text-brand-700 dark:text-brand-300">
            {activeCount} aktīvi
          </span>
        )}
      </div>

      <Field label="Avots">
        <select
          value={value.source || ''}
          onChange={(e) => update('source', e.target.value)}
          className={selectClass}
        >
          <option value="">Visi avoti</option>
          {Object.entries(SOURCE_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
      </Field>

      <Field label="Dokumenta veids">
        <select
          value={value.doc_type || ''}
          onChange={(e) => update('doc_type', e.target.value)}
          className={selectClass}
        >
          <option value="">Visi veidi</option>
          {Object.entries(DOC_TYPE_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
      </Field>

      <Field label="Statuss">
        <select
          value={value.status || ''}
          onChange={(e) => update('status', e.target.value)}
          className={selectClass}
        >
          <option value="">Jebkurš</option>
          {Object.entries(STATUS_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
      </Field>

      <Field label="Tēma">
        <select
          value={value.topic || ''}
          onChange={(e) => update('topic', e.target.value)}
          className={selectClass}
        >
          <option value="">Visas tēmas</option>
          {topics.map(({ topic }) => (
            <option key={topic} value={topic}>
              {TOPIC_LABELS[topic] || topic}
            </option>
          ))}
        </select>
      </Field>

      <Field label="Iestāde">
        <input
          type="text"
          value={value.issuer || ''}
          onChange={(e) => update('issuer', e.target.value)}
          placeholder="Piem. Saeima"
          className={inputClass}
        />
      </Field>

      <div className="grid grid-cols-2 gap-2">
        <Field label="No datuma">
          <input
            type="date"
            value={value.date_from || ''}
            onChange={(e) => update('date_from', e.target.value)}
            className={inputClass}
          />
        </Field>
        <Field label="Līdz datumam">
          <input
            type="date"
            value={value.date_to || ''}
            onChange={(e) => update('date_to', e.target.value)}
            className={inputClass}
          />
        </Field>
      </div>

      <button
        onClick={() => onChange({})}
        disabled={activeCount === 0}
        className={
          'w-full text-sm px-3 py-1.5 rounded-md border transition-colors ' +
          (activeCount === 0
            ? 'border-slate-200 dark:border-slate-800 text-slate-400 cursor-not-allowed'
            : 'border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800')
        }
      >
        Notīrīt filtrus
      </button>
    </aside>
  )
}

function Field({ label, children }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
        {label}
      </label>
      {children}
    </div>
  )
}

const selectClass =
  'w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20'

const inputClass =
  'w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20'
