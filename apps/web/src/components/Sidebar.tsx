import {
  BarChart3,
  ChevronLeft,
  Database,
  FlaskConical,
  Gauge,
  List,
  Settings,
  SlidersHorizontal,
  WalletCards,
} from 'lucide-react'

const items = [
  [Gauge, 'Overview'],
  [FlaskConical, 'Strategies'],
  [SlidersHorizontal, 'Backtests'],
  [BarChart3, 'Results'],
  [WalletCards, 'Positions'],
  [List, 'Trade Log'],
  [Database, 'Data'],
  [Settings, 'Settings'],
] as const

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">QV</span>
        <div><strong>Vol Backtester</strong><small>Command Center</small></div>
      </div>
      <nav aria-label="Primary navigation">
        {items.map(([Icon, label], index) => (
          <button className={index === 0 ? 'nav-item active' : 'nav-item'} key={label}>
            <Icon size={18} strokeWidth={1.7} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <button className="collapse"><ChevronLeft size={18} /> Collapse</button>
    </aside>
  )
}

