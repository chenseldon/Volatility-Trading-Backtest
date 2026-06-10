# Trading Command Center Design Specification

## Product

The dashboard is an interview-ready research terminal for configuring and running
SPY options volatility backtests. It is not a brokerage interface and never claims
that synthetic results are live or executable.

## Visual Target

The accepted concept is `trading-command-center.png` at 1488 x 1058. The UI uses a
near-black graphite canvas, cool cyan analysis accents, restrained green/red
performance semantics, amber risk warnings, thin dividers, and compact typography.

## Layout

- A 174 px left navigation rail anchors the product identity and primary sections.
- The top command bar contains ticker, date range, strategy, data source, run action,
  and run status.
- Six horizontal KPI cells lead the content area.
- Equity and drawdown share the primary chart panel.
- IV percentile and realized volatility form the secondary synchronized chart.
- Risk and exposure remain visible in a fixed right rail.
- Positions and trade records use dense, border-separated tables at the bottom.
- Parameters open in a right-side drawer rather than displacing result charts.

## Design Tokens

| Token | Value |
| --- | --- |
| Canvas | `#061018` |
| Surface | `#0a151e` |
| Surface raised | `#0d1b25` |
| Border | `#1d303b` |
| Text | `#edf6fb` |
| Muted | `#8da1ad` |
| Cyan | `#18c8ff` |
| Blue action | `#087cf0` |
| Positive | `#39d875` |
| Negative | `#ff4d50` |
| Warning | `#f2b84b` |
| Radius | `4px` |

Typography uses Inter with system sans-serif fallbacks. Body and control text are
13-14 px, labels are 11-12 px uppercase, and metric values are 23-26 px.

## Required Interactions

- Run a backtest and preserve form state on errors.
- Change dataset, date range, strategy, and all advanced parameters.
- Upload and validate a CSV option chain.
- Switch Positions, Trades, Comparison, and Assumptions tabs.
- Hover linked charts and inspect signal points.
- Download generated reports and data artifacts.
- Collapse navigation and open/close the parameter drawer.

## Disclosure

Every sample run must display `Synthetic option-chain data`. Reports must document
Black-Scholes pricing, no early exercise, Reg-T style margin approximation, execution
at bid/ask plus slippage, and the difference between delta-neutral and direction-free.

