from pathlib import Path

import pandas as pd

from volbacktest.data import generate_synthetic_chain
from volbacktest.models import BacktestConfig, SignalConfig
from volbacktest.service import BacktestService


def test_service_persists_result_and_report_artifacts(tmp_path: Path) -> None:
    chain = generate_synthetic_chain(periods=90, seed=5)
    dates = sorted(chain["date"].unique())
    config = BacktestConfig(
        start_date=pd.Timestamp(dates[0]).date(),
        end_date=pd.Timestamp(dates[-1]).date(),
        signal=SignalConfig(low_percentile=40, high_percentile=60, zscore_threshold=0),
    )
    service = BacktestService(output_dir=tmp_path)

    result = service.run(config, chain=chain)

    run_dir = tmp_path / result.run_id
    assert (run_dir / "result.json").exists()
    assert (run_dir / "report.md").exists()
    assert (run_dir / "equity.png").exists()
    assert (run_dir / "drawdown.png").exists()
    assert service.get(result.run_id).metrics == result.metrics
    assert service.list_runs()[0]["run_id"] == result.run_id

    sweep = service.sweep(
        config,
        {"strategy.max_holding_days": [5, 10]},
        chain=chain,
    )
    assert len(sweep) == 2
    assert (tmp_path / "latest-sweep.json").exists()
    assert (tmp_path / "latest-sweep.csv").exists()
