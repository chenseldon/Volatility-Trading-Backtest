from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from volbacktest.models import BacktestResult


def write_report_artifacts(result: BacktestResult, run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = result.model_dump(mode="json")
    (run_dir / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (run_dir / "report.md").write_text(_markdown_report(result), encoding="utf-8")
    _write_rows(run_dir / "trades.csv", result.trades)
    _write_rows(run_dir / "legs.csv", result.legs)

    equity = pd.DataFrame(result.equity_curve)
    _plot_series(
        equity,
        "equity",
        run_dir / "equity.png",
        "Strategy Equity Curve",
        "#18c8ff",
    )
    _plot_series(
        equity,
        "drawdown",
        run_dir / "drawdown.png",
        "Strategy Drawdown",
        "#ff4d50",
    )


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in rows for key in row}))
        writer.writeheader()
        writer.writerows(rows)


def _plot_series(
    frame: pd.DataFrame, column: str, path: Path, title: str, color: str
) -> None:
    fig, axis = plt.subplots(figsize=(12, 4.5), facecolor="#061018")
    axis.set_facecolor("#0a151e")
    axis.plot(pd.to_datetime(frame["date"]), frame[column], color=color, linewidth=1.4)
    axis.set_title(title, color="#edf6fb")
    axis.tick_params(colors="#8da1ad")
    axis.grid(color="#1d303b", alpha=0.55, linewidth=0.6)
    for spine in axis.spines.values():
        spine.set_color("#1d303b")
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def _markdown_report(result: BacktestResult) -> str:
    metrics = result.metrics
    return f"""# Volatility Strategy Backtest Report

**Run ID:** `{result.run_id}`  
**Strategy:** `{result.config.strategy.name.value}`  
**Data source:** `{result.data_source}`

## Performance

| Metric | Value |
| --- | ---: |
| Annualized return | {metrics["annualized_return"]:.2%} |
| Sharpe ratio | {metrics["sharpe_ratio"]:.2f} |
| Maximum drawdown | {metrics["max_drawdown"]:.2%} |
| Win rate | {metrics["win_rate"]:.2%} |
| Profit factor | {metrics["profit_factor"]:.2f} |
| Closed trades | {int(metrics["trade_count"])} |

## Assumptions and limitations

- Bundled examples use synthetic option-chain data.
- SPY options are American-style; this model uses Black-Scholes and does not model
  early exercise.
- Short-option margin is a disclosed Reg-T style approximation, not a broker quote.
- Executions use bid/ask plus configured slippage and commissions.
- Delta hedging reduces first-order directional exposure; it does not remove gamma,
  vega, gap, liquidity, or model risk.
"""

