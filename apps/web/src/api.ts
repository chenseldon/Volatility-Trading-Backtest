import type { BacktestForm, BacktestResult } from './types'

export async function runBacktest(form: BacktestForm): Promise<BacktestResult> {
  const response = await fetch('/api/v1/backtests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset: 'synthetic',
      start_date: form.startDate,
      end_date: form.endDate,
      strategy: {
        name: form.strategy,
        target_dte: form.targetDte,
        min_exit_dte: 5,
        max_holding_days: form.maxHoldingDays,
        delta_hedge: form.deltaHedge,
      },
      signal: {
        low_percentile: form.lowPercentile,
        high_percentile: form.highPercentile,
        zscore_threshold: form.zscoreThreshold,
        exit_low: 40,
        exit_high: 60,
      },
      risk: {
        initial_capital: 250000,
        risk_per_trade: form.riskPerTrade,
        max_margin_fraction: form.maxMargin,
        max_positions: 5,
        stop_loss: form.stopLoss,
        profit_target: form.profitTarget,
        commission_per_contract: form.commission,
        slippage_bps: form.slippageBps,
      },
    }),
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail?.message ?? payload?.detail ?? 'Backtest request failed')
  }
  return response.json()
}

