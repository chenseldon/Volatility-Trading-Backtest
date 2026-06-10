import pandas as pd

from volbacktest.data import generate_synthetic_chain
from volbacktest.engine import run_backtest
from volbacktest.models import BacktestConfig, SignalConfig, StrategyName, StrategySpec


def test_backtest_is_deterministic_and_executes_after_signal_day() -> None:
    chain = generate_synthetic_chain(periods=180, seed=11)
    dates = sorted(chain["date"].unique())
    config = BacktestConfig(
        start_date=pd.Timestamp(dates[0]).date(),
        end_date=pd.Timestamp(dates[-1]).date(),
        strategy=StrategySpec(name=StrategyName.SHORT_STRANGLE, delta_hedge=True),
        signal=SignalConfig(low_percentile=40, high_percentile=60, zscore_threshold=0),
    )

    first = run_backtest(chain, config)
    second = run_backtest(chain, config)

    assert first.metrics == second.metrics
    assert first.trades == second.trades
    assert first.metrics["trade_count"] > 0
    entry = next(trade for trade in first.trades if trade["event"] == "open")
    factor_dates = {
        row["date"]: row for row in first.factors if row["iv_percentile_60"] is not None
    }
    previous_date = max(date for date in factor_dates if date < entry["date"])
    assert factor_dates[previous_date]["signal"] in {"long_vol", "short_vol"}
    assert entry["signal_date"] == previous_date

