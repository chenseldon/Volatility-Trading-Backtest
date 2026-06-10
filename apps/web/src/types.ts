export type Metrics = {
  annualized_return: number
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  profit_factor: number
  trade_count: number
}

export type EquityPoint = { date: string; equity: number; drawdown: number }
export type FactorPoint = {
  date: string
  underlying_price: number | null
  implied_volatility: number | null
  rv20: number | null
  iv_percentile_20: number | null
  iv_percentile_60: number | null
  iv_rv_zscore: number | null
  signal: string
}
export type ExposurePoint = {
  date: string
  delta: number
  vega: number
  margin_used: number
  open_positions: number
}
export type Trade = {
  date: string
  event: string
  strategy: string
  signal?: string
  reason?: string
  pnl: number
  signal_date: string
}

export type BacktestResult = {
  run_id: string
  status: string
  data_source: string
  metrics: Metrics
  equity_curve: EquityPoint[]
  factors: FactorPoint[]
  exposures: ExposurePoint[]
  trades: Trade[]
  legs: Record<string, unknown>[]
  warnings: string[]
  config: {
    risk?: {
      initial_capital?: number
      stop_loss?: number
      profit_target?: number
    }
    signal?: {
      exit_low?: number
      exit_high?: number
    }
  }
}

export type BacktestForm = {
  dataset: string
  startDate: string
  endDate: string
  strategy: string
  lowPercentile: number
  highPercentile: number
  zscoreThreshold: number
  targetDte: number
  maxHoldingDays: number
  deltaHedge: boolean
  riskPerTrade: number
  maxMargin: number
  stopLoss: number
  profitTarget: number
  commission: number
  slippageBps: number
}
