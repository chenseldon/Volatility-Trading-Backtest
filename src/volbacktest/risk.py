from __future__ import annotations

import math
from collections.abc import Iterable, Mapping

from volbacktest.models import RiskConfig, StrategyName

CONTRACT_MULTIPLIER = 100


def reg_t_margin(
    strategy: StrategyName,
    legs: Iterable[Mapping[str, float | int | str]],
    spot: float,
) -> float:
    records = list(legs)
    if strategy in {StrategyName.BULL_CALL_SPREAD, StrategyName.BEAR_PUT_SPREAD}:
        strikes = [float(leg["strike"]) for leg in records]
        width = max(strikes) - min(strikes)
        premium_cashflow = sum(
            -int(leg["quantity"]) * float(leg["price"]) * CONTRACT_MULTIPLIER
            for leg in records
        )
        return max(width * CONTRACT_MULTIPLIER - max(premium_cashflow, 0), 0.0)

    if all(int(leg["quantity"]) > 0 for leg in records):
        return sum(
            int(leg["quantity"]) * float(leg["price"]) * CONTRACT_MULTIPLIER
            for leg in records
        )

    margin = 0.0
    for leg in records:
        if int(leg["quantity"]) >= 0:
            continue
        strike = float(leg["strike"])
        premium = float(leg["price"])
        option_type = str(leg["option_type"])
        otm = max(spot - strike, 0) if option_type == "put" else max(strike - spot, 0)
        per_share = max(0.20 * spot - otm + premium, 0.10 * spot + premium)
        margin += abs(int(leg["quantity"])) * per_share * CONTRACT_MULTIPLIER
    return margin


def position_size(
    risk: RiskConfig,
    risk_per_contract: float,
    margin_per_contract: float,
    equity: float | None = None,
) -> int:
    account = risk.initial_capital if equity is None else equity
    if risk_per_contract <= 0 or margin_per_contract <= 0:
        return 0
    risk_limit = account * risk.risk_per_trade
    margin_limit = account * risk.max_margin_fraction
    return max(
        min(
            math.floor(risk_limit / risk_per_contract),
            math.floor(margin_limit / margin_per_contract),
        ),
        0,
    )
