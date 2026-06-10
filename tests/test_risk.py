import pytest

from volbacktest.models import RiskConfig, StrategyName
from volbacktest.risk import position_size, reg_t_margin


def test_short_strangle_margin_uses_reg_t_proxy() -> None:
    legs = [
        {"option_type": "put", "strike": 95, "quantity": -1, "price": 2.0},
        {"option_type": "call", "strike": 105, "quantity": -1, "price": 2.2},
    ]

    margin = reg_t_margin(StrategyName.SHORT_STRANGLE, legs, spot=100)

    assert margin == pytest.approx(3_420)


def test_position_size_respects_risk_and_margin_budgets() -> None:
    risk = RiskConfig(initial_capital=100_000, risk_per_trade=0.02, max_margin_fraction=0.40)

    assert position_size(risk, risk_per_contract=500, margin_per_contract=1_000) == 4
    assert position_size(risk, risk_per_contract=5_000, margin_per_contract=1_000) == 0
