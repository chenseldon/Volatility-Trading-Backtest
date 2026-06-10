import type { BacktestResult } from './types'

const dates = Array.from({ length: 120 }, (_, index) => {
  const date = new Date(2024, 0, 2 + index * 2)
  return date.toISOString().slice(0, 10)
})

const equity = dates.map((date, index) => {
  const trend = index * 620
  const cycle = Math.sin(index / 7) * 3500
  const shock = index > 66 && index < 80 ? -9000 + (index - 66) * 500 : 0
  const value = 250000 + trend + cycle + shock
  return { date, equity: value, drawdown: Math.min(0, -Math.abs(Math.sin(index / 9)) * 0.075) }
})

const factors = dates.map((date, index) => ({
  date,
  underlying_price: 470 + index * 0.55 + Math.sin(index / 5) * 7,
  implied_volatility: 0.21 + Math.sin(index / 8) * 0.055,
  rv20: 0.17 + Math.sin(index / 10 + 1) * 0.035,
  iv_percentile_20: 50 + Math.sin(index / 8) * 42,
  iv_percentile_60: 50 + Math.sin(index / 11) * 38,
  iv_rv_zscore: Math.sin(index / 8) * 1.8,
  signal: index % 29 === 0 ? 'short_vol' : index % 37 === 0 ? 'long_vol' : 'neutral',
}))

export const sampleResult: BacktestResult = {
  run_id: 'sample-run',
  status: 'completed',
  data_source: 'synthetic',
  metrics: {
    annualized_return: 0.1876,
    sharpe_ratio: 1.42,
    max_drawdown: -0.1283,
    win_rate: 0.6427,
    profit_factor: 1.78,
    trade_count: 64,
  },
  equity_curve: equity,
  factors,
  exposures: dates.map((date, index) => ({
    date,
    delta: Math.sin(index / 4) * 0.08,
    vega: -18420 + Math.sin(index / 5) * 2200,
    margin_used: 62845 + Math.sin(index / 6) * 7000,
    open_positions: index % 9 < 5 ? 1 : 0,
  })),
  trades: [
    { date: '2024-12-31', event: 'close', strategy: 'short_strangle', reason: 'mean_reversion', pnl: 412.5, signal_date: '2024-12-30' },
    { date: '2024-12-24', event: 'open', strategy: 'short_strangle', signal: 'short_vol', pnl: 0, signal_date: '2024-12-23' },
    { date: '2024-12-17', event: 'close', strategy: 'short_strangle', reason: 'profit_target', pnl: 365, signal_date: '2024-12-10' },
  ],
  legs: [
    { option_type: 'put', strike: 590, quantity: -2, entry_price: 3.24, expiry: '2025-01-17' },
    { option_type: 'call', strike: 610, quantity: -2, entry_price: 3.05, expiry: '2025-01-17' },
  ],
  warnings: ['Synthetic option-chain data; results are not live trading performance.'],
  config: {},
}

