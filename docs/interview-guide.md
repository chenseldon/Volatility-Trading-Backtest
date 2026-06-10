# Interview Guide

## 30-second project summary

I built a reproducible options-volatility trading research system rather than only a
pricing notebook. It converts IV percentile and IV-versus-realized-volatility
dislocations into straddle, strangle, and vertical-spread positions, executes signals
one day later, models transaction costs and margin, optionally delta hedges, and judges
the result through Sharpe ratio, drawdown, win rate, payoff ratio, and trade-level P&L.

## Why volatility mean reversion is not enough

High IV can remain high during a regime shift. The strategy therefore requires both an
IV percentile extreme and an IV-RV z-score confirmation. Results must still be tested
across thresholds and market states; a backtest is evidence about a model, not proof of
a permanent arbitrage.

## Neutral versus directional strategies

- A straddle or strangle is not direction-free by itself. Its delta changes as spot
  moves, so the engine can rebalance SPY shares daily.
- Delta hedging removes only first-order directional exposure. Gamma, vega, jumps,
  liquidity, and discrete-hedging error remain.
- Bull call and bear put spreads deliberately retain directional exposure and have
  bounded maximum loss.

## Risk discussion

- Position size is limited by both a percentage risk budget and a portfolio margin cap.
- Naked short-option margin uses a disclosed Reg-T style approximation.
- Stops, targets, DTE, and maximum holding period prevent indefinite exposure.
- Maximum drawdown is emphasized because short-volatility strategies can show frequent
  small wins followed by rare large losses.

## Honest limitations

The bundled chain is synthetic, SPY early exercise is not modeled, bid/ask liquidity is
simplified, and daily data misses intraday path dependence. A production version would
use licensed historical chains, corporate-action-aware rates/dividends, broker margin,
and event-driven intraday execution.

