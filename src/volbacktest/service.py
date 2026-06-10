from __future__ import annotations

import json
import re
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from volbacktest.data import generate_synthetic_chain, load_option_chain_csv, validate_option_chain
from volbacktest.engine import run_backtest
from volbacktest.models import BacktestConfig, BacktestResult
from volbacktest.report import write_report_artifacts
from volbacktest.sweep import run_parameter_sweep


class BacktestService:
    def __init__(self, output_dir: str | Path = "outputs/runs") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self, config: BacktestConfig, chain: pd.DataFrame | None = None
    ) -> BacktestResult:
        market = chain if chain is not None else self._load_dataset(config)
        result = run_backtest(market, config)
        write_report_artifacts(result, self.output_dir / result.run_id)
        return result

    def save_dataset(self, filename: str, content: bytes) -> dict[str, Any]:
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(filename).name).strip(".-")
        if not safe_name:
            safe_name = "option-chain.csv"
        validated = validate_option_chain(pd.read_csv(BytesIO(content)))
        dataset_id = uuid4().hex
        dataset_dir = self.output_dir / "datasets"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        validated.to_csv(dataset_dir / f"{dataset_id}.csv", index=False)
        return {
            "valid": True,
            "dataset": f"upload:{dataset_id}",
            "name": safe_name,
            "rows": len(validated),
            "columns": list(validated.columns),
        }

    def sweep(
        self,
        config: BacktestConfig,
        parameter_grid: dict[str, list[Any]],
        chain: pd.DataFrame | None = None,
    ) -> list[dict[str, Any]]:
        market = chain if chain is not None else self._load_dataset(config)
        rows = run_parameter_sweep(market, config, parameter_grid)
        path = self.output_dir / "latest-sweep.json"
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        csv_rows = [
            {
                **row["parameters"],
                **{key: value for key, value in row.items() if key != "parameters"},
            }
            for row in rows
        ]
        pd.DataFrame(csv_rows).to_csv(self.output_dir / "latest-sweep.csv", index=False)
        return rows

    def get(self, run_id: str) -> BacktestResult:
        path = self._run_dir(run_id) / "result.json"
        if not path.exists():
            raise FileNotFoundError(run_id)
        return BacktestResult.model_validate_json(path.read_text(encoding="utf-8"))

    def list_runs(self) -> list[dict[str, Any]]:
        rows = []
        for path in self.output_dir.glob("*/result.json"):
            result = BacktestResult.model_validate_json(path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "run_id": result.run_id,
                    "strategy": result.config.strategy.name.value,
                    "status": result.status,
                    "data_source": result.data_source,
                    "metrics": result.metrics,
                }
            )
        return sorted(rows, key=lambda row: row["run_id"], reverse=True)

    def artifact(self, run_id: str, name: str) -> Path:
        allowed = {
            "result.json",
            "report.md",
            "trades.csv",
            "legs.csv",
            "equity.png",
            "drawdown.png",
        }
        if name not in allowed:
            raise FileNotFoundError(name)
        path = self._run_dir(run_id) / name
        if not path.exists():
            raise FileNotFoundError(name)
        return path

    def _run_dir(self, run_id: str) -> Path:
        if not run_id.isalnum():
            raise FileNotFoundError(run_id)
        return self.output_dir / run_id

    def _load_dataset(self, config: BacktestConfig) -> pd.DataFrame:
        if config.dataset == "synthetic":
            periods = len(pd.bdate_range(config.start_date, config.end_date))
            return generate_synthetic_chain(config.start_date.isoformat(), periods, config.seed)
        if config.dataset.startswith("upload:"):
            dataset_id = config.dataset.removeprefix("upload:")
            if len(dataset_id) != 32 or not dataset_id.isalnum():
                raise FileNotFoundError("invalid uploaded dataset")
            path = self.output_dir / "datasets" / f"{dataset_id}.csv"
            if not path.exists():
                raise FileNotFoundError("uploaded dataset not found")
            return load_option_chain_csv(str(path))
        return load_option_chain_csv(config.dataset)
