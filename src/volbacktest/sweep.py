from __future__ import annotations

import itertools
from typing import Any

import pandas as pd

from volbacktest.engine import run_backtest
from volbacktest.models import BacktestConfig


def _set_dotted(payload: dict[str, Any], path: str, value: Any) -> None:
    target = payload
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value


def run_parameter_sweep(
    chain: pd.DataFrame,
    base_config: BacktestConfig,
    parameter_grid: dict[str, list[Any]],
) -> list[dict[str, Any]]:
    names = list(parameter_grid)
    rows: list[dict[str, Any]] = []
    for values in itertools.product(*(parameter_grid[name] for name in names)):
        parameters = dict(zip(names, values, strict=True))
        payload = base_config.model_dump(mode="python")
        for path, value in parameters.items():
            _set_dotted(payload, path, value)
        result = run_backtest(chain, BacktestConfig.model_validate(payload))
        rows.append(
            {
                "run_id": result.run_id,
                "parameters": parameters,
                **result.metrics,
            }
        )
    rows.sort(key=lambda row: row["sharpe_ratio"], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows

