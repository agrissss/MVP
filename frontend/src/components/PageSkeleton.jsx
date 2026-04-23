/**
 * Vispārīgs ielādes placeholders lapām un kartīšu režģiem.
 * Izmanto .skeleton CSS klasi (šimmer animācija definēta index.css).
 */
export default function PageSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="skeleton h-8 w-2/3" />
      <div className="skeleton h-4 w-1/2" />
      <div className="grid md:grid-cols-2 gap-3 mt-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="rounded-xl border border-slate-200/70 dark:border-slate-800/70 bg-white/60 dark:bg-slate-900/60 p-4 space-y-3">
      <div className="flex gap-2">
        <div className="skeleton h-4 w-16" />
        <div className="skeleton h-4 w-14" />
      </div>
      <div className="skeleton h-5 w-5/6" />
      <div className="skeleton h-4 w-2/3" />
      <div className="skeleton h-4 w-full" />
    </div>
  )
}

export function ListSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton h-12 w-full" />
      ))}
    </div>
  )
}
