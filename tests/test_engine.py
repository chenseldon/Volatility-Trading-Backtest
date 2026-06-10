import pandas as pd

from volbacktest.data import generate_synthetic_chain
from volbacktest.engine import _strategy_accepts_signal, run_backtest
from volbacktest.models import (
    BacktestConfig,
    RiskConfig,
    SignalConfig,
    StrategyName,
    StrategySpec,
)


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
    assert {"entry_delta", "entry_gamma", "entry_vega", "entry_theta"}.issubset(
        first.legs[0]
    )


def test_backtest_supports_bounded_concurrent_positions() -> None:
    chain = generate_synthetic_chain(periods=180, seed=11)
    dates = sorted(chain["date"].unique())
    config = BacktestConfig(
        start_date=pd.Timestamp(dates[0]).date(),
        end_date=pd.Timestamp(dates[-1]).date(),
        strategy=StrategySpec(
            name=StrategyName.SHORT_STRANGLE,
            max_holding_days=10,
            delta_hedge=False,
        ),
        signal=SignalConfig(
            low_percentile=40,
            high_percentile=60,
            zscore_threshold=0,
            exit_low=0,
            exit_high=1,
        ),
        risk=RiskConfig(
            max_positions=3,
            max_margin_fraction=0.4,
            stop_loss=10,
            profit_target=10,
        ),
    )

    result = run_backtest(chain, config)

    assert max(row["open_positions"] for row in result.exposures) == 3
    assert max(row["margin_used"] for row in result.exposures) <= 100_000
    assert any(
        trade["event"] == "limit" and trade["reason"] == "max_positions"
        for trade in result.trades
    )


def test_debit_vertical_spreads_only_accept_low_volatility_signals() -> None:
    assert _strategy_accepts_signal(StrategyName.BULL_CALL_SPREAD, "long_vol")
    assert _strategy_accepts_signal(StrategyName.BEAR_PUT_SPREAD, "long_vol")
    assert not _strategy_accepts_signal(StrategyName.BEAR_PUT_SPREAD, "short_vol")
