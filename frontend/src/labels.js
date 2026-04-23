// Cilvēkam lasāmi nosaukumi dažādām kodu vērtībām.

export const DOC_TYPE_LABELS = {
  likums: 'Likums',
  mk_noteikumi: 'MK noteikumi',
  instrukcija: 'Instrukcija',
  vadlinijas: 'Vadlīnijas',
  datu_kopa: 'Datu kopa',
  pazinojums: 'Paziņojums',
  cits: 'Cits',
}

export const STATUS_LABELS = {
  speka: 'Spēkā',
  zaudejis_speku: 'Zaudējis spēku',
  grozits: 'Grozīts',
  nezinams: 'Nezināms',
}

export const STATUS_COLORS = {
  speka: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  zaudejis_speku: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300',
  grozits: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  nezinams: 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
}

export const TOPIC_LABELS = {
  nodokli: 'Nodokļi',
  gramatvediba: 'Grāmatvedība',
  darba_tiesibas: 'Darba tiesības',
  logistika: 'Loģistika',
  transports: 'Transports',
  muita: 'Muita',
  e_komercija: 'E-komercija',
  datu_aizsardziba: 'Datu aizsardzība',
  komercdarbiba: 'Komercdarbība',
  publiskie_iepirkumi: 'Publiskie iepirkumi',
}

export const TOPIC_ICONS = {
  nodokli: '💶',
  gramatvediba: '📒',
  darba_tiesibas: '👥',
  logistika: '📦',
  transports: '🚚',
  muita: '🛃',
  e_komercija: '🛒',
  datu_aizsardziba: '🔒',
  komercdarbiba: '🏢',
  publiskie_iepirkumi: '📄',
}

export const SOURCE_LABELS = {
  likumi_lv: 'likumi.lv',
  data_gov_lv: 'data.gov.lv',
  vid: 'VID',
  atd: 'ATD',
}

export const SECTION_LEVEL_LABELS = {
  sadala: 'Sadaļa',
  nodala: 'Nodaļa',
  pants: 'Pants',
  dala: 'Daļa',
  punkts: 'Punkts',
  apakspunkts: 'Apakšpunkts',
}

export function formatSectionLabel(section) {
  const num = section.number
  switch (section.level) {
    case 'pants': return `${num}. pants`
    case 'dala': return `${num}. daļa`
    case 'punkts': return `${num}. punkts`
    case 'apakspunkts': return `${num}. apakšpunkts`
    case 'nodala': return `${num}. nodaļa`
    case 'sadala': return `${num}. sadaļa`
    default: return num
  }
}

export const RELATION_LABELS = {
  implements: 'piemēro',
  amends: 'groza',
  replaces: 'aizvieto',
  related: 'saistīts ar',
  references: 'atsaucas uz',
}

export function formatDate(d) {
  if (!d) return '—'
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return d
  return dt.toLocaleDateString('lv-LV', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

export function formatDateTime(d) {
  if (!d) return '—'
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return d
  return dt.toLocaleString('lv-LV', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}
