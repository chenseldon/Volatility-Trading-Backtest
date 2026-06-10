from __future__ import annotations

import numpy as np
import pandas as pd


def _last_percentile(values: np.ndarray) -> float:
    current = values[-1]
    return float(np.mean(values <= current) * 100)


def compute_volatility_factors(market: pd.DataFrame) -> pd.DataFrame:
    frame = market[["date", "underlying_price", "implied_volatility"]].copy()
    frame = frame.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    returns = np.log(frame["underlying_price"]).diff()
    frame["rv20"] = returns.rolling(20, min_periods=20).std() * np.sqrt(252)
    frame["iv_percentile_20"] = frame["implied_volatility"].rolling(
        20, min_periods=20
    ).apply(_last_percentile, raw=True)
    frame["iv_percentile_60"] = frame["implied_volatility"].rolling(
        60, min_periods=60
    ).apply(_last_percentile, raw=True)
    spread = frame["implied_volatility"] - frame["rv20"]
    rolling_mean = spread.rolling(60, min_periods=40).mean()
    rolling_std = spread.rolling(60, min_periods=40).std()
    frame["iv_rv_zscore"] = (spread - rolling_mean) / rolling_std.replace(0, np.nan)
    return frame

