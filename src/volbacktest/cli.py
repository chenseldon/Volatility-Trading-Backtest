from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from volbacktest.data import load_option_chain_csv
from volbacktest.models import BacktestConfig
from volbacktest.service import BacktestService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="volbacktest")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-data")
    validate.add_argument("path")

    run = subparsers.add_parser("run")
    run.add_argument("--config")
    run.add_argument("--output-dir", default="outputs/runs")

    sweep = subparsers.add_parser("sweep")
    sweep.add_argument("--config")
    sweep.add_argument("--grid", required=True)
    sweep.add_argument("--output-dir", default="outputs/runs")

    report = subparsers.add_parser("report")
    report.add_argument("run_id")
    report.add_argument("--output-dir", default="outputs/runs")
    return parser


def _load_config(path: str | None) -> BacktestConfig:
    if path is None:
        return BacktestConfig()
    return BacktestConfig.model_validate_json(Path(path).read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-data":
        frame = load_option_chain_csv(args.path)
        print(json.dumps({"valid": True, "rows": len(frame)}))
        return 0

    service = BacktestService(args.output_dir)
    if args.command == "run":
        result = service.run(_load_config(args.config))
        print(json.dumps({"run_id": result.run_id, "metrics": result.metrics}))
    elif args.command == "sweep":
        grid = json.loads(Path(args.grid).read_text(encoding="utf-8"))
        print(json.dumps(service.sweep(_load_config(args.config), grid)))
    elif args.command == "report":
        print(service.artifact(args.run_id, "report.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
