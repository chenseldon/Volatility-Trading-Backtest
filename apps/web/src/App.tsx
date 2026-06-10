import { lazy, Suspense, useState } from 'react'

import { runBacktest } from './api'
import { CommandBar } from './components/CommandBar'
import { DataTabs } from './components/DataTabs'
import { MetricsStrip } from './components/MetricsStrip'
import { ParameterDrawer } from './components/ParameterDrawer'
import { RiskPanel } from './components/RiskPanel'
import { Sidebar } from './components/Sidebar'
import { sampleResult } from './sampleData'
import type { BacktestForm, BacktestResult } from './types'
import './styles.css'

const Charts = lazy(() => import('./components/Charts').then((module) => ({ default: module.Charts })))

const initialForm: BacktestForm = {
  startDate: '2024-01-02', endDate: '2024-06-30', strategy: 'short_strangle',
  lowPercentile: 20, highPercentile: 80, zscoreThreshold: 1, targetDte: 30,
  maxHoldingDays: 10, deltaHedge: true, riskPerTrade: 0.02, maxMargin: 0.4,
  stopLoss: 0.2, profitTarget: 0.25, commission: 0.65, slippageBps: 1,
}

export default function App() {
  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState<BacktestResult>(sampleResult)
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [error, setError] = useState('')

  const handleRun = async () => {
    setStatus('running')
    setError('')
    try {
      setResult(await runBacktest(form))
      setStatus('completed')
    } catch (requestError) {
      setStatus('error')
      setError(requestError instanceof Error ? requestError.message : 'Backtest failed')
    }
  }

  return (
    <main className="app-shell">
      <Sidebar />
      <div className="workspace">
        <CommandBar form={form} setForm={setForm} status={status} onRun={handleRun} onParameters={() => setDrawerOpen(true)} />
        {error ? <div className="error-banner">{error}</div> : null}
        <div className="content-grid">
          <div className="analysis-column">
            <MetricsStrip metrics={result.metrics} />
            <Suspense fallback={<div className="chart-loading">Loading analytics…</div>}>
              <Charts result={result} />
            </Suspense>
            <DataTabs result={result} />
          </div>
          <RiskPanel result={result} />
        </div>
        <footer><span className="connected-dot" /> Backtest Engine: <strong>Connected</strong><span>Python 3.12</span><span>Risk model: SPY</span><span>Slippage: {form.slippageBps.toFixed(1)} bps</span><span>Commission: ${form.commission.toFixed(2)}/contract</span><em>Synthetic option-chain data</em></footer>
      </div>
      <ParameterDrawer open={drawerOpen} form={form} setForm={setForm} onClose={() => setDrawerOpen(false)} />
    </main>
  )
}
