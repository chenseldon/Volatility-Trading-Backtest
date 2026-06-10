import pandas as pd

from volbacktest.factors import compute_volatility_factors


def test_volatility_factors_use_only_current_and_past_rows() -> None:
    dates = pd.bdate_range("2024-01-02", periods=90)
    base = pd.DataFrame(
        {
            "date": dates,
            "underlying_price": 100 + pd.Series(range(90)) * 0.15,
            "implied_volatility": 0.2 + pd.Series(range(90)) * 0.001,
        }
    )
    changed = base.copy()
    changed.loc[70:, "underlying_price"] *= 1.5
    changed.loc[70:, "implied_volatility"] = 0.8

    original_factors = compute_volatility_factors(base)
    changed_factors = compute_volatility_factors(changed)

    pd.testing.assert_frame_equal(original_factors.iloc[:70], changed_factors.iloc[:70])
    assert {"rv20", "iv_percentile_20", "iv_percentile_60", "iv_rv_zscore"}.issubset(
        original_factors
    )

