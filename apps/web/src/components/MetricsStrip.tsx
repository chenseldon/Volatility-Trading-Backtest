import type { Metrics } from '../types'

const percent = (value: number) => `${(value * 100).toFixed(2)}%`

export function MetricsStrip({ metrics }: { metrics: Metrics }) {
  const rows = [
    ['Annualized return', percent(metrics.annualized_return), 'CAGR', 'positive'],
    ['Sharpe ratio', metrics.sharpe_ratio.toFixed(2), 'risk adjusted', 'positive'],
    ['Max drawdown', percent(metrics.max_drawdown), 'peak to trough', 'negative'],
    ['Win rate', percent(metrics.win_rate), 'closed trades', 'positive'],
    ['Profit factor', metrics.profit_factor.toFixed(2), 'gross P/L', 'positive'],
    ['Trades', String(metrics.trade_count), 'completed', 'neutral'],
  ]
  return (
    <section className="metrics-strip">
      {rows.map(([label, value, note, tone]) => (
        <article key={label}><span>{label}</span><strong className={tone}>{value}</strong><small>{note}</small></article>
      ))}
    </section>
  )
}

