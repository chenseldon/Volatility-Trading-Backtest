# Option Chain CSV Contract

Required UTF-8 CSV columns:

| Column | Type | Rules |
| --- | --- | --- |
| `date` | date | Quote date in ISO `YYYY-MM-DD` format |
| `expiry` | date | Must be later than `date` |
| `option_type` | string | `call` or `put` |
| `strike` | float | Strictly positive |
| `bid` | float | Non-negative and no greater than `ask` |
| `ask` | float | Strictly positive |
| `implied_volatility` | float | Annualized decimal, `(0, 5]` |
| `underlying_price` | float | Strictly positive |

Optional columns are `delta`, `gamma`, `vega`, `theta`, `risk_free_rate`, and
`dividend_yield`. Missing Greeks are recomputed with Black-Scholes. Imported market
quotes always use bid/ask for valuation and execution.

