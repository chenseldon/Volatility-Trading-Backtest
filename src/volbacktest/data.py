from __future__ import annotations

import numpy as np
import pandas as pd

from volbacktest.pricing import black_scholes

REQUIRED_COLUMNS = {
    "date",
    "expiry",
    "option_type",
    "strike",
    "bid",
    "ask",
    "implied_volatility",
    "underlying_price",
}


class DataValidationError(ValueError):
    pass


def validate_option_chain(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise DataValidationError(f"missing columns: {', '.join(sorted(missing))}")

    validated = frame.copy()
    validated["date"] = pd.to_datetime(validated["date"]).dt.normalize()
    validated["expiry"] = pd.to_datetime(validated["expiry"]).dt.normalize()
    numeric_columns = [
        "strike",
        "bid",
        "ask",
        "implied_volatility",
        "underlying_price",
    ]
    for column in numeric_columns:
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
    if (
        validated[numeric_columns].isna().any(axis=None)
        or not np.isfinite(validated[numeric_columns].to_numpy()).all()
    ):
        raise DataValidationError("numeric quote fields must contain valid numbers")
    if (~validated["option_type"].isin(["call", "put"])).any():
        raise DataValidationError("option_type must be call or put")
    if (validated["expiry"] <= validated["date"]).any():
        raise DataValidationError("expiry must be after date")
    if (validated["bid"] > validated["ask"]).any():
        raise DataValidationError("bid cannot exceed ask")
    if (
        (validated["strike"] <= 0).any()
        or (validated["bid"] < 0).any()
        or (validated["ask"] <= 0).any()
        or (validated["underlying_price"] <= 0).any()
        or (validated["implied_volatility"] <= 0).any()
        or (validated["implied_volatility"] > 5).any()
    ):
        raise DataValidationError("quote values are outside the supported range")
    for column in ("delta", "gamma", "vega", "theta"):
        if column not in validated:
            validated[column] = np.nan
        else:
            validated[column] = pd.to_numeric(validated[column], errors="coerce")
    missing_greeks = validated[["delta", "gamma", "vega", "theta"]].isna().any(axis=1)
    for index, row in validated.loc[missing_greeks].iterrows():
        tte = max((row["expiry"] - row["date"]).days, 1) / 365
        risk_free_rate = row.get("risk_free_rate", 0.03)
        dividend_yield = row.get("dividend_yield", 0.012)
        greeks = black_scholes(
            float(row["underlying_price"]),
            float(row["strike"]),
            tte,
            float(risk_free_rate) if pd.notna(risk_free_rate) else 0.03,
            float(dividend_yield) if pd.notna(dividend_yield) else 0.012,
            float(row["implied_volatility"]),
            str(row["option_type"]),
        )
        validated.loc[index, ["delta", "gamma", "vega", "theta"]] = [
            greeks.delta,
            greeks.gamma,
            greeks.vega,
            greeks.theta,
        ]
    return validated.sort_values(["date", "expiry", "strike", "option_type"]).reset_index(drop=True)


def _next_friday(day: pd.Timestamp, minimum_days: int) -> pd.Timestamp:
    target = day + pd.Timedelta(days=minimum_days)
    return target + pd.Timedelta(days=(4 - target.weekday()) % 7)


def generate_synthetic_chain(
    start: str | pd.Timestamp = "2020-01-02",
    periods: int = 420,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=periods)
    log_returns = np.empty(periods)
    iv = np.empty(periods)
    log_returns[0] = 0.0
    iv[0] = 0.22
    regime = 0
    for index in range(1, periods):
        if rng.random() < 0.025:
            regime = 1 - regime
        realized = 0.12 if regime == 0 else 0.30
        log_returns[index] = rng.normal(0.00025, realized / np.sqrt(252))
        target_iv = realized + (0.055 if regime else 0.035)
        next_iv = iv[index - 1] + 0.12 * (target_iv - iv[index - 1]) + rng.normal(0, 0.012)
        iv[index] = np.clip(next_iv, 0.08, 0.85)

    spots = 320 * np.exp(np.cumsum(log_returns))
    rows: list[dict[str, object]] = []
    for day, spot, base_iv in zip(dates, spots, iv, strict=True):
        strike_step = 5.0
        center = round(spot / strike_step) * strike_step
        strikes = np.arange(center - 50, center + 51, strike_step)
        for dte in (21, 35, 56):
            expiry = _next_friday(day, dte)
            tte = max((expiry - day).days, 1) / 365
            for strike in strikes:
                moneyness = strike / spot - 1
                for option_type in ("call", "put"):
                    skew = (-0.28 * moneyness) if option_type == "put" else (-0.08 * moneyness)
                    term = 0.012 * np.log1p(dte / 30)
                    quote_iv = float(np.clip(base_iv + skew + term, 0.06, 1.5))
                    greeks = black_scholes(spot, strike, tte, 0.03, 0.012, quote_iv, option_type)
                    spread = max(0.02, 0.035 * greeks.price + 0.01)
                    rows.append(
                        {
                            "date": day,
                            "expiry": expiry,
                            "option_type": option_type,
                            "strike": float(strike),
                            "bid": round(max(greeks.price - spread / 2, 0.01), 4),
                            "ask": round(greeks.price + spread / 2, 4),
                            "implied_volatility": quote_iv,
                            "underlying_price": float(spot),
                            "delta": greeks.delta,
                            "gamma": greeks.gamma,
                            "vega": greeks.vega,
                            "theta": greeks.theta,
                        }
                    )
    return pd.DataFrame(rows)


def load_option_chain_csv(path: str) -> pd.DataFrame:
    return validate_option_chain(pd.read_csv(path))
