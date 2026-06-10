from __future__ import annotations

import pandas as pd

from volbacktest.models import StrategyName, StrategySpec


def _nearest_expiry(chain: pd.DataFrame, target_dte: int) -> pd.Timestamp:
    date = chain["date"].iloc[0]
    expiries = pd.Series(chain["expiry"].unique())
    return min(expiries, key=lambda expiry: abs((pd.Timestamp(expiry) - date).days - target_dte))


def _nearest_delta(options: pd.DataFrame, target: float) -> pd.Series:
    return options.loc[(options["delta"] - target).abs().idxmin()]


def select_legs(chain: pd.DataFrame, spec: StrategySpec) -> pd.DataFrame:
    if chain.empty:
        raise ValueError("no option quotes available")
    day = chain[chain["date"] == chain["date"].min()].copy()
    expiry = _nearest_expiry(day, spec.target_dte)
    options = day[day["expiry"] == expiry]
    spot = float(options["underlying_price"].iloc[0])
    calls = options[options["option_type"] == "call"]
    puts = options[options["option_type"] == "put"]

    selections: list[tuple[pd.Series, int]]
    if spec.name in {StrategyName.LONG_STRADDLE, StrategyName.SHORT_STRADDLE}:
        if calls.empty or puts.empty:
            raise ValueError("straddle requires both call and put contracts")
        atm_call = calls.loc[(calls["strike"] - spot).abs().idxmin()]
        atm_put = puts.loc[(puts["strike"] - spot).abs().idxmin()]
        quantity = 1 if spec.name == StrategyName.LONG_STRADDLE else -1
        selections = [(atm_call, quantity), (atm_put, quantity)]
    elif spec.name in {StrategyName.LONG_STRANGLE, StrategyName.SHORT_STRANGLE}:
        if calls.empty or puts.empty:
            raise ValueError("strangle requires both call and put contracts")
        quantity = 1 if spec.name == StrategyName.LONG_STRANGLE else -1
        selections = [
            (_nearest_delta(puts, -0.25), quantity),
            (_nearest_delta(calls, 0.25), quantity),
        ]
    elif spec.name == StrategyName.BULL_CALL_SPREAD:
        if len(calls) < 2:
            raise ValueError("bull call spread requires at least two call contracts")
        selections = [(_nearest_delta(calls, 0.40), 1), (_nearest_delta(calls, 0.20), -1)]
    elif spec.name == StrategyName.BEAR_PUT_SPREAD:
        if len(puts) < 2:
            raise ValueError("bear put spread requires at least two put contracts")
        selections = [(_nearest_delta(puts, -0.40), 1), (_nearest_delta(puts, -0.20), -1)]
    else:
        raise ValueError(f"unsupported strategy: {spec.name}")

    records = []
    for quote, quantity in selections:
        record = quote.to_dict()
        record["quantity"] = quantity
        records.append(record)
    return pd.DataFrame(records).sort_values(["option_type", "strike"]).reset_index(drop=True)
