import { lazy, Suspense, useState } from 'react'

import { runBacktest, uploadDataset } from './api'
import { CommandBar } from './components/CommandBar'
import { DataTabs } from './components/DataTabs'
import { MetricsStrip } from './components/MetricsStrip'
import { ParameterDrawer } from './components/ParameterDrawer'
import { RiskPanel } from './components/RiskPanel'
import { Sidebar } from './components/Sidebar'
import { sampleResult } from './sampleData'
import type { BacktestForm, BacktestResult } from './types'
import './styles.css'

const Charts = lazy(() =>
  import('./components/Charts').then((module) => ({ default: module.Charts })),
)

const initialForm: BacktestForm = {
  dataset: 'synthetic',
  startDate: '2024-01-02',
  endDate: '2024-06-30',
  strategy: 'short_strangle',
  lowPercentile: 20,
  highPercentile: 80,
  zscoreThreshold: 1,
  targetDte: 30,
  maxHoldingDays: 10,
  deltaHedge: true,
  riskPerTrade: 0.02,
  maxMargin: 0.4,
  stopLoss: 0.2,
  profitTarget: 0.25,
  commission: 0.65,
  slippageBps: 1,
}

export default function App() {
  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState<BacktestResult>(sampleResult)
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [error, setError] = useState('')
  const [datasetName, setDatasetName] = useState('Synthetic (regime model)')

  const handleRun = async () => {
    if (form.startDate >= form.endDate) {
      setStatus('error')
      setError('End date must be after start date')
      return
    }
    if (form.lowPercentile >= form.highPercentile) {
      setStatus('error')
      setError('Low IV percentile must be below high IV percentile')
      return
    }
    if (
      form.riskPerTrade <= 0 ||
      form.riskPerTrade > 1 ||
      form.maxMargin <= 0 ||
      form.maxMargin > 1
    ) {
      setStatus('error')
      setError('Risk per trade and maximum margin must be between 0 and 1')
      return
    }
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

  const handleUpload = async (file: File) => {
    setError('')
    try {
      const uploaded = await uploadDataset(file)
      setForm((current) => ({ ...current, dataset: uploaded.dataset }))
      setDatasetName(`${uploaded.name} (${uploaded.rows.toLocaleString()} rows)`)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Dataset upload failed')
    }
  }

  const sourceDisclosure =
    form.dataset === 'synthetic'
      ? 'Synthetic option-chain data'
      : `Imported CSV: ${datasetName}`

  return (
    <main className="app-shell">
      <Sidebar />
      <div className="workspace">
        <CommandBar
          form={form}
          setForm={setForm}
          status={status}
          datasetName={datasetName}
          onUpload={handleUpload}
          onRun={handleRun}
          onParameters={() => setDrawerOpen(true)}
        />
        {error ? <div className="error-banner">{error}</div> : null}
        <div className="content-grid">
          <div className="analysis-column">
            <MetricsStrip metrics={result.metrics} />
            <Suspense fallback={<div className="chart-loading">Loading analytics...</div>}>
              <Charts result={result} />
            </Suspense>
            <DataTabs result={result} />
          </div>
          <RiskPanel result={result} />
        </div>
        <footer>
          <span className="connected-dot" /> Backtest Engine: <strong>Connected</strong>
          <span>Python 3.12</span>
          <span>Risk model: SPY</span>
          <span>Slippage: {form.slippageBps.toFixed(1)} bps</span>
          <span>Commission: ${form.commission.toFixed(2)}/contract</span>
          <em>{sourceDisclosure}</em>
        </footer>
      </div>
      <ParameterDrawer
        open={drawerOpen}
        form={form}
        setForm={setForm}
        onClose={() => setDrawerOpen(false)}
      />
    </main>
  )
}
