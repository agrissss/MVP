import { Link } from 'react-router-dom'

export default function Breadcrumb({ items }) {
  return (
    <nav aria-label="Breadcrumb" className="text-sm text-slate-600 dark:text-slate-400 mb-4">
      <ol className="flex items-center gap-1 flex-wrap">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-1">
            {i > 0 && <span aria-hidden="true">›</span>}
            {item.to ? (
              <Link to={item.to} className="hover:text-brand-600 dark:hover:text-brand-500">
                {item.label}
              </Link>
            ) : (
              <span className="text-slate-900 dark:text-slate-100">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
