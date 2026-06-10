import { X } from 'lucide-react'

import type { BacktestForm } from '../types'

type Props = { open: boolean; form: BacktestForm; setForm: (form: BacktestForm) => void; onClose: () => void }

export function ParameterDrawer({ open, form, setForm, onClose }: Props) {
  if (!open) return null
  const numberField = (label: string, key: keyof BacktestForm, step = 1) => (
    <label><span>{label}</span><input type="number" step={step} value={String(form[key])} onChange={(event) => setForm({ ...form, [key]: Number(event.target.value) })} /></label>
  )
  return (
    <div className="drawer-backdrop" onMouseDown={onClose}>
      <aside className="parameter-drawer" role="dialog" aria-label="Backtest parameters" onMouseDown={(event) => event.stopPropagation()}>
        <header><div><h2>Backtest parameters</h2><p>Execution, signal and risk controls</p></div><button aria-label="Close parameters" onClick={onClose}><X size={18} /></button></header>
        <section><h3>Volatility signal</h3>{numberField('Low IV percentile', 'lowPercentile')}{numberField('High IV percentile', 'highPercentile')}{numberField('IV-RV z-score', 'zscoreThreshold', 0.1)}</section>
        <section><h3>Contract selection</h3>{numberField('Target DTE', 'targetDte')}{numberField('Maximum holding days', 'maxHoldingDays')}<label className="toggle-row"><span>Daily delta hedge</span><input type="checkbox" checked={form.deltaHedge} onChange={(event) => setForm({ ...form, deltaHedge: event.target.checked })} /></label></section>
        <section><h3>Risk & execution</h3>{numberField('Risk per trade', 'riskPerTrade', 0.01)}{numberField('Maximum margin', 'maxMargin', 0.05)}{numberField('Stop loss', 'stopLoss', 0.05)}{numberField('Profit target', 'profitTarget', 0.05)}{numberField('Commission / contract', 'commission', 0.05)}{numberField('Slippage (bps)', 'slippageBps', 0.5)}</section>
      </aside>
    </div>
  )
}

