import pandas as pd
import pytest

from volbacktest.performance import calculate_performance


def test_performance_calculates_standard_metrics() -> None:
    equity = pd.Series(
        [100_000, 101_000, 99_000, 103_000, 104_000],
        index=pd.bdate_range("2025-01-02", periods=5),
    )
    trades = pd.DataFrame({"pnl": [500.0, -200.0, 700.0]})

    metrics = calculate_performance(equity, trades)

    assert metrics["annualized_return"] > 0
    assert metrics["max_drawdown"] < 0
    assert metrics["win_rate"] == pytest.approx(2 / 3)
    assert metrics["profit_factor"] == pytest.approx(6.0)
    assert metrics["trade_count"] == 3
