# Volatility Strategy Backtest Report

**Run ID:** `ae3ea4af0eb6`  
**Strategy:** `short_strangle`  
**Data source:** `synthetic`

## Performance

| Metric | Value |
| --- | ---: |
| Annualized return | 2.71% |
| Sharpe ratio | 1.22 |
| Maximum drawdown | -0.76% |
| Win rate | 70.00% |
| Payoff ratio | 1.52 |
| Profit factor | 3.55 |
| Closed trades | 20 |

## Assumptions and limitations

- Bundled examples use synthetic option-chain data.
- SPY options are American-style; this model uses Black-Scholes and does not model
  early exercise.
- Short-option margin is a disclosed Reg-T style approximation, not a broker quote.
- Executions use bid/ask plus configured slippage and commissions.
- Delta hedging reduces first-order directional exposure; it does not remove gamma,
  vega, gap, liquidity, or model risk.
