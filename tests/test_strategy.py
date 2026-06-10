import pytest

from volbacktest.data import generate_synthetic_chain
from volbacktest.models import StrategyName, StrategySpec
from volbacktest.strategy import select_legs


def test_short_strangle_selects_otm_call_and_put() -> None:
    chain = generate_synthetic_chain(periods=1, seed=3)
    day = chain[chain["date"] == chain["date"].min()]
    spec = StrategySpec(name=StrategyName.SHORT_STRANGLE, target_dte=30)

    legs = select_legs(day, spec)

    spot = day["underlying_price"].iloc[0]
    assert len(legs) == 2
    assert set(legs["option_type"]) == {"call", "put"}
    assert (legs["quantity"] == -1).all()
    assert legs.loc[legs["option_type"] == "put", "strike"].iloc[0] < spot
    assert legs.loc[legs["option_type"] == "call", "strike"].iloc[0] > spot


def test_bull_call_spread_has_bounded_structure() -> None:
    chain = generate_synthetic_chain(periods=1, seed=3)
    spec = StrategySpec(name=StrategyName.BULL_CALL_SPREAD)

    legs = select_legs(chain, spec)

    assert list(legs.sort_values("strike")["quantity"]) == [1, -1]
    assert set(legs["option_type"]) == {"call"}


def test_strategy_reports_missing_option_sides_precisely() -> None:
    chain = generate_synthetic_chain(periods=1, seed=2)
    calls_only = chain[chain["option_type"] == "call"]

    with pytest.raises(ValueError, match="requires both call and put"):
        select_legs(calls_only, StrategySpec(name=StrategyName.LONG_STRADDLE))
