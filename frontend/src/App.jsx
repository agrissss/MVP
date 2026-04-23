import { Routes, Route, NavLink, Link } from 'react-router-dom'
import { useEffect, useState, lazy, Suspense } from 'react'
import PageSkeleton from './components/PageSkeleton.jsx'

// Route-level code splitting — katra lapa savā bundle, ielādē pēc pieprasījuma
const Dashboard       = lazy(() => import('./pages/Dashboard.jsx'))
const Search          = lazy(() => import('./pages/Search.jsx'))
const DocumentDetail  = lazy(() => import('./pages/DocumentDetail.jsx'))
const Sources         = lazy(() => import('./pages/Sources.jsx'))
const Topic           = lazy(() => import('./pages/Topic.jsx'))

function ThemeToggle() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'))
  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [dark])
  return (
    <button
      onClick={() => setDark(!dark)}
      className="relative inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-colors"
      title={dark ? 'Pārslēgt uz gaišo režīmu' : 'Pārslēgt uz tumšo režīmu'}
      aria-label="Pārslēgt tēmu"
    >
      <span aria-hidden className="text-[14px]">{dark ? '☀' : '☾'}</span>
      <span className="hidden sm:inline">{dark ? 'Gaišais' : 'Tumšais'}</span>
    </button>
  )
}

function Disclaimer() {
  return (
    <div className="bg-amber-50/80 dark:bg-amber-950/30 border-b border-amber-200/60 dark:border-amber-800/50 text-amber-900 dark:text-amber-200 text-xs">
      <div className="max-w-6xl mx-auto px-4 py-1.5 flex items-center gap-2">
        <span aria-hidden>⚠</span>
        <span>
          Šis rīks <strong className="font-semibold">nav juridiska konsultācija</strong>.
          Autoritatīvais teksts vienmēr ir oficiālajā avotā.
        </span>
      </div>
    </div>
  )
}

function NavBar() {
  const linkClass = ({ isActive }) =>
    `px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
      isActive
        ? 'bg-brand-600 text-white shadow-soft'
        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
    }`
  return (
    <header className="glass bg-white/80 dark:bg-slate-950/70 border-b border-slate-200/70 dark:border-slate-800/70 sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4 flex-wrap">
        <Link to="/" className="flex items-center gap-2 whitespace-nowrap group">
          <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-white text-sm shadow-soft group-hover:scale-105 transition-transform">
            ⚖
          </span>
          <span className="font-semibold text-[15px] tracking-tight">
            Tiesību aktu pārlūks
          </span>
        </Link>
        <nav className="flex gap-1 flex-1">
          <NavLink to="/" end className={linkClass}>Pārskats</NavLink>
          <NavLink to="/meklet" className={linkClass}>Meklēt</NavLink>
          <NavLink to="/avoti" className={linkClass}>Avoti</NavLink>
        </nav>
        <ThemeToggle />
      </div>
    </header>
  )
}

function Footer() {
  return (
    <footer className="border-t border-slate-200/70 dark:border-slate-800/70 mt-16">
      <div className="max-w-6xl mx-auto px-4 py-8 text-sm text-slate-600 dark:text-slate-400 space-y-1">
        <p>
          Sistēma izmanto tikai <strong className="font-semibold">oficiālus publiskus avotus</strong>:
          likumi.lv, data.gov.lv, VID, ATD. Katram ierakstam ir saite uz oficiālo publikāciju.
        </p>
        <p>
          MVP v0.1.0 · <Link to="/avoti" className="text-brand-600 dark:text-brand-400 hover:underline">Avotu saraksts</Link>
        </p>
      </div>
    </footer>
  )
}

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Disclaimer />
      <NavBar />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full animate-fade-in">
        <Suspense fallback={<PageSkeleton />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/meklet" element={<Search />} />
            <Route path="/dokuments/:id" element={<DocumentDetail />} />
            <Route path="/avoti" element={<Sources />} />
            <Route path="/tema/:code" element={<Topic />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
    </div>
  )
}
