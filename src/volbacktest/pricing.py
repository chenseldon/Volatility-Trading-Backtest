from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Greeks:
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float


def _norm_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def _norm_pdf(value: float) -> float:
    return math.exp(-0.5 * value * value) / math.sqrt(2 * math.pi)


def black_scholes(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
    option_type: str,
) -> Greeks:
    if min(spot, strike, volatility) <= 0 or time_to_expiry <= 0:
        intrinsic = max(spot - strike, 0) if option_type == "call" else max(strike - spot, 0)
        delta = float(spot > strike) if option_type == "call" else -float(spot < strike)
        return Greeks(intrinsic, delta, 0.0, 0.0, 0.0)

    root_time = math.sqrt(time_to_expiry)
    d1 = (
        math.log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry
    ) / (volatility * root_time)
    d2 = d1 - volatility * root_time
    spot_discount = math.exp(-dividend_yield * time_to_expiry)
    strike_discount = math.exp(-risk_free_rate * time_to_expiry)

    if option_type == "call":
        price = spot * spot_discount * _norm_cdf(d1) - strike * strike_discount * _norm_cdf(d2)
        delta = spot_discount * _norm_cdf(d1)
        theta = (
            -(spot * spot_discount * _norm_pdf(d1) * volatility) / (2 * root_time)
            - risk_free_rate * strike * strike_discount * _norm_cdf(d2)
            + dividend_yield * spot * spot_discount * _norm_cdf(d1)
        ) / 365
    elif option_type == "put":
        price = strike * strike_discount * _norm_cdf(-d2) - spot * spot_discount * _norm_cdf(-d1)
        delta = spot_discount * (_norm_cdf(d1) - 1)
        theta = (
            -(spot * spot_discount * _norm_pdf(d1) * volatility) / (2 * root_time)
            + risk_free_rate * strike * strike_discount * _norm_cdf(-d2)
            - dividend_yield * spot * spot_discount * _norm_cdf(-d1)
        ) / 365
    else:
        raise ValueError("option_type must be call or put")

    gamma = spot_discount * _norm_pdf(d1) / (spot * volatility * root_time)
    vega = spot * spot_discount * _norm_pdf(d1) * root_time / 100
    return Greeks(price=max(price, 0.0), delta=delta, gamma=gamma, vega=vega, theta=theta)

