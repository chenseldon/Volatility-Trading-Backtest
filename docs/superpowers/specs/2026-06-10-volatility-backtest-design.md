# Volatility Trading Backtest Design

This specification records the approved architecture and product decisions.

- Python is the single source of truth for data, strategy, execution, risk, metrics,
  and reporting.
- FastAPI is a thin synchronous transport over `BacktestService`.
- React/Vite implements the approved Trading Command Center.
- Synthetic SPY chains are deterministic and prominently disclosed.
- Imported CSV chains follow `docs/data-contract.md`.
- Signals use 20/60-day IV percentiles and a 60-day z-score of IV minus RV20.
- Trades are generated at close and executed on the following trading day.
- Supported strategies are long/short straddles, long/short strangles, bull call
  spreads, and bear put spreads.
- Delta hedging is optional and charged execution costs.
- Risk is limited by per-trade budget, portfolio margin usage, concurrent positions,
  stop loss, profit target, DTE, and maximum holding period.
- Reports include assumptions, limitations, metrics, chart data, trades, and legs.

