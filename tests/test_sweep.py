import pandas as pd

from volbacktest.data import generate_synthetic_chain
from volbacktest.models import BacktestConfig, SignalConfig, StrategyName, StrategySpec
from volbacktest.sweep import run_parameter_sweep


def test_parameter_sweep_returns_ranked_runs() -> None:
    chain = generate_synthetic_chain(periods=100, seed=8)
    dates = sorted(chain["date"].unique())
    config = BacktestConfig(
        start_date=pd.Timestamp(dates[0]).date(),
        end_date=pd.Timestamp(dates[-1]).date(),
        strategy=StrategySpec(name=StrategyName.SHORT_STRANGLE),
        signal=SignalConfig(low_percentile=40, high_percentile=60, zscore_threshold=0),
    )

    rows = run_parameter_sweep(chain, config, {"strategy.max_holding_days": [5, 10]})

    assert len(rows) == 2
    assert rows[0]["rank"] == 1
    assert rows[0]["sharpe_ratio"] >= rows[1]["sharpe_ratio"]
    assert {row["parameters"]["strategy.max_holding_days"] for row in rows} == {5, 10}

