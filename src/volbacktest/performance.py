from __future__ import annotations

import math

import pandas as pd


def calculate_performance(equity: pd.Series, trades: pd.DataFrame) -> dict[str, float]:
    returns = equity.pct_change().dropna()
    years = max(len(returns) / 252, 1 / 252)
    annualized_return = float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)
    volatility = float(returns.std(ddof=1) * math.sqrt(252)) if len(returns) > 1 else 0.0
    sharpe = float(returns.mean() / returns.std(ddof=1) * math.sqrt(252)) if volatility else 0.0
    drawdown = equity / equity.cummax() - 1
    pnl = trades["pnl"] if not trades.empty and "pnl" in trades else pd.Series(dtype=float)
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    gross_profit = float(wins.sum())
    gross_loss = abs(float(losses.sum()))
    win_rate = float((pnl > 0).mean()) if len(pnl) else 0.0
    payoff_ratio = float(wins.mean() / abs(losses.mean())) if len(wins) and len(losses) else 0.0
    return {
        "annualized_return": annualized_return,
        "max_drawdown": float(drawdown.min()),
        "sharpe_ratio": sharpe,
        "annualized_volatility": volatility,
        "win_rate": win_rate,
        "payoff_ratio": payoff_ratio,
        "profit_factor": gross_profit / gross_loss if gross_loss else 0.0,
        "trade_count": int(len(pnl)),
    }
