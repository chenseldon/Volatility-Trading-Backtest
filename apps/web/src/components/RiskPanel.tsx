import type { BacktestResult } from '../types'

const money = (value: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value)

export function RiskPanel({ result }: { result: BacktestResult }) {
  const exposure = result.exposures.at(-1) ?? {
    delta: 0.03,
    vega: -18420,
    margin_used: 62845,
    open_positions: 1,
  }
  const capital = result.config.risk?.initial_capital ?? 250000
  const stopLoss = result.config.risk?.stop_loss ?? 0.2
  const profitTarget = result.config.risk?.profit_target ?? 0.25
  const exitLow = result.config.signal?.exit_low ?? 40
  const exitHigh = result.config.signal?.exit_high ?? 60
  const marginPct = Math.min((exposure.margin_used / capital) * 100, 100)
  const reportUrl =
    result.run_id === 'sample-run'
      ? '#'
      : `/api/v1/artifacts/${result.run_id}/report.md`

  return (
    <aside className="risk-panel">
      <h2>Risk & Exposure</h2>
      <section>
        <h3>Delta hedge</h3>
        <dl>
          <div><dt>Status</dt><dd className="positive">{Math.abs(exposure.delta) < 0.1 ? 'Hedged' : 'Open'}</dd></div>
          <div><dt>Net delta</dt><dd>{exposure.delta.toFixed(2)}</dd></div>
          <div><dt>Hedge method</dt><dd>SPY shares</dd></div>
          <div><dt>Open positions</dt><dd>{exposure.open_positions}</dd></div>
        </dl>
      </section>
      <section>
        <h3>Margin</h3>
        <dl>
          <div><dt>Buying power</dt><dd>{money(capital)}</dd></div>
          <div><dt>Margin used</dt><dd>{money(exposure.margin_used)}</dd></div>
          <div><dt>Margin usage</dt><dd>{marginPct.toFixed(2)}%</dd></div>
        </dl>
        <div className="meter"><span style={{ width: `${marginPct}%` }} /></div>
      </section>
      <section>
        <h3>Position risk</h3>
        <dl>
          <div><dt>Portfolio delta</dt><dd>{exposure.delta.toFixed(2)}</dd></div>
          <div><dt>Portfolio vega</dt><dd>{exposure.vega.toFixed(0)}</dd></div>
          <div><dt>Max drawdown</dt><dd className="negative">{(result.metrics.max_drawdown * 100).toFixed(2)}%</dd></div>
          <div><dt>Model</dt><dd>Reg-T proxy</dd></div>
        </dl>
      </section>
      <section>
        <h3>Stops & targets</h3>
        <dl>
          <div><dt>Stop loss</dt><dd>{(stopLoss * 100).toFixed(2)}%</dd></div>
          <div><dt>Profit target</dt><dd>{(profitTarget * 100).toFixed(2)}%</dd></div>
          <div><dt>IV exit band</dt><dd>{exitLow}-{exitHigh}%</dd></div>
        </dl>
      </section>
      <a className="risk-link" href={reportUrl} download={result.run_id === 'sample-run' ? undefined : 'report.md'}>
        Download Full Risk Report
      </a>
    </aside>
  )
}
