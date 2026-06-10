# Architecture

## Boundaries

`volbacktest` is the only layer allowed to contain trading logic. The CLI and FastAPI
instantiate `BacktestService`; the React application only sends typed configuration and
renders returned result objects.

## Data flow

1. Validate an imported chain or generate a deterministic synthetic chain.
2. Aggregate daily IV and spot, then calculate RV20, IV percentiles, and IV-RV z-score.
3. Generate a signal at the close of day T.
4. Select option legs and execute at bid/ask plus slippage on T+1.
5. Mark up to the configured number of concurrent positions daily, rebalance each
   position's delta if enabled, and apply risk exits.
6. Calculate metrics and serialize equity, drawdown, factors, Greeks, margin, trades,
   legs, warnings, and configuration.
7. Write artifacts and return the same result through the CLI or API.

## Failure behavior

- Invalid dates and parameters are rejected by Pydantic with field-level errors.
- CSV failures identify missing columns or invalid rows.
- Empty date ranges and unavailable chains fail before a run is persisted.
- New positions are sized against both per-trade risk and remaining portfolio margin.
- Artifact names are allow-listed and run IDs cannot contain path separators.
- The web client preserves form state and displays API errors without replacing the
  previous successful result.
