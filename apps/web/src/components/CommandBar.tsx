import { CalendarDays, Play, Settings2 } from 'lucide-react'

import type { BacktestForm } from '../types'

type Props = {
  form: BacktestForm
  setForm: (form: BacktestForm) => void
  status: 'idle' | 'running' | 'completed' | 'error'
  onRun: () => void
  onParameters: () => void
}

export function CommandBar({ form, setForm, status, onRun, onParameters }: Props) {
  return (
    <header className="command-bar">
      <label className="control ticker"><span>Ticker</span><select><option>SPY</option></select></label>
      <label className="control date-control">
        <span>Date range</span>
        <div><input type="date" value={form.startDate} onChange={(event) => setForm({ ...form, startDate: event.target.value })} />
          <span>→</span>
          <input type="date" value={form.endDate} onChange={(event) => setForm({ ...form, endDate: event.target.value })} />
          <CalendarDays size={16} />
        </div>
      </label>
      <label className="control strategy-control"><span>Strategy</span>
        <select value={form.strategy} onChange={(event) => setForm({ ...form, strategy: event.target.value })}>
          <option value="short_strangle">Short Strangle (30D)</option>
          <option value="short_straddle">Short Straddle</option>
          <option value="long_straddle">Long Straddle</option>
          <option value="long_strangle">Long Strangle</option>
          <option value="bull_call_spread">Bull Call Spread</option>
          <option value="bear_put_spread">Bear Put Spread</option>
        </select>
      </label>
      <label className="control source-control"><span>Data source</span><select><option>Synthetic (regime model)</option></select></label>
      <button className="secondary-button" type="button" onClick={onParameters}><Settings2 size={16} /> Parameters</button>
      <button className="run-button" type="button" disabled={status === 'running'} onClick={onRun}>
        <Play size={16} fill="currentColor" /> {status === 'running' ? 'Running…' : 'Run Backtest'}
      </button>
      <div className={`run-status ${status}`}>
        <span>Status</span><strong>{status === 'idle' ? 'Ready' : status[0].toUpperCase() + status.slice(1)}</strong>
      </div>
    </header>
  )
}

