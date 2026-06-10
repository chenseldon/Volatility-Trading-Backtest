import pandas as pd
import pytest

from volbacktest.data import DataValidationError, generate_synthetic_chain, validate_option_chain


def test_synthetic_chain_is_deterministic() -> None:
    first = generate_synthetic_chain(periods=80, seed=7)
    second = generate_synthetic_chain(periods=80, seed=7)

    pd.testing.assert_frame_equal(first, second)
    assert {"date", "expiry", "option_type", "strike", "bid", "ask"}.issubset(first)
    assert len(first) > 1_000


def test_option_chain_rejects_crossed_market() -> None:
    frame = pd.DataFrame(
        [
            {
                "date": "2025-01-02",
                "expiry": "2025-02-21",
                "option_type": "call",
                "strike": 100,
                "bid": 4,
                "ask": 3,
                "implied_volatility": 0.2,
                "underlying_price": 100,
            }
        ]
    )

    with pytest.raises(DataValidationError, match="bid cannot exceed ask"):
        validate_option_chain(frame)


def test_option_chain_recomputes_missing_greeks() -> None:
    frame = pd.DataFrame(
        [
            {
                "date": "2025-01-02",
                "expiry": "2025-02-21",
                "option_type": "call",
                "strike": 100,
                "bid": 4,
                "ask": 4.2,
                "implied_volatility": 0.2,
                "underlying_price": 100,
            }
        ]
    )

    validated = validate_option_chain(frame)

    assert validated.loc[0, "delta"] > 0
    assert validated.loc[0, "gamma"] > 0
    assert validated.loc[0, "vega"] > 0
    assert validated.loc[0, "theta"] < 0
