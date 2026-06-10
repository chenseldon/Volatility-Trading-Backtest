import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
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

export type NavigationItem = (typeof items)[number][1]

type Props = {
  active: NavigationItem
  collapsed: boolean
  onNavigate: (item: NavigationItem) => void
  onToggleCollapsed: () => void
}

export function Sidebar({ active, collapsed, onNavigate, onToggleCollapsed }: Props) {
  return (
    <aside className={collapsed ? 'sidebar collapsed' : 'sidebar'}>
      <div className="brand">
        <span className="brand-mark">QV</span>
        <div><strong>Vol Backtester</strong><small>Command Center</small></div>
      </div>
      <nav aria-label="Primary navigation">
        {items.map(([Icon, label]) => (
          <button
            aria-current={active === label ? 'page' : undefined}
            aria-label={collapsed ? label : undefined}
            className={active === label ? 'nav-item active' : 'nav-item'}
            key={label}
            onClick={() => onNavigate(label)}
            title={collapsed ? label : undefined}
            type="button"
          >
            <Icon size={18} strokeWidth={1.7} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <button
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        className="collapse"
        onClick={onToggleCollapsed}
        type="button"
      >
        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        <span>{collapsed ? 'Expand' : 'Collapse'}</span>
      </button>
    </aside>
  )
}

