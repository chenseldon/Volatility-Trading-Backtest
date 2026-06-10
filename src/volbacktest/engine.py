from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import pandas as pd

from volbacktest.data import validate_option_chain
from volbacktest.factors import compute_volatility_factors
from volbacktest.models import BacktestConfig, BacktestResult, StrategyName
from volbacktest.performance import calculate_performance
from volbacktest.pricing import black_scholes
from volbacktest.risk import position_size, reg_t_margin
from volbacktest.strategy import select_legs

CONTRACT_MULTIPLIER = 100


@dataclass
class Position:
    opened: pd.Timestamp
    signal_date: pd.Timestamp
    signal: str
    legs: pd.DataFrame
    entry_cashflow: float
    entry_cost_basis: float
    commission: float
    margin: float
    hedge_shares: float = 0.0
    hedge_pnl: float = 0.0
    previous_spot: float = 0.0


def _signal(row: pd.Series, config: BacktestConfig) -> str:
    values = row[["iv_percentile_20", "iv_percentile_60", "iv_rv_zscore"]]
    if values.isna().any():
        return "neutral"
    if (
        row["iv_percentile_20"] >= config.signal.high_percentile
        and row["iv_percentile_60"] >= config.signal.high_percentile
        and row["iv_rv_zscore"] >= config.signal.zscore_threshold
    ):
        return "short_vol"
    if (
        row["iv_percentile_20"] <= config.signal.low_percentile
        and row["iv_percentile_60"] <= config.signal.low_percentile
        and row["iv_rv_zscore"] <= -config.signal.zscore_threshold
    ):
        return "long_vol"
    return "neutral"


def _strategy_accepts_signal(name: StrategyName, signal: str) -> bool:
    if name in {StrategyName.SHORT_STRADDLE, StrategyName.SHORT_STRANGLE}:
        return signal == "short_vol"
    if name in {StrategyName.LONG_STRADDLE, StrategyName.LONG_STRANGLE}:
        return signal == "long_vol"
    if name == StrategyName.BULL_CALL_SPREAD:
        return signal == "long_vol"
    return signal == "short_vol"


def _execution_price(row: pd.Series, quantity: int, opening: bool, slippage_bps: float) -> float:
    buying = quantity > 0 if opening else quantity < 0
    base = float(row["ask"] if buying else row["bid"])
    slip = base * slippage_bps / 10_000
    return base + slip if buying else max(base - slip, 0.0)


def _current_quote(leg: pd.Series, day_chain: pd.DataFrame) -> pd.Series:
    exact = day_chain[
        (day_chain["expiry"] == leg["expiry"])
        & (day_chain["option_type"] == leg["option_type"])
        & (day_chain["strike"] == leg["strike"])
    ]
    if not exact.empty:
        return exact.iloc[0]

    spot = float(day_chain["underlying_price"].iloc[0])
    iv = float(day_chain["implied_volatility"].median())
    dte = max((pd.Timestamp(leg["expiry"]) - pd.Timestamp(day_chain["date"].iloc[0])).days, 0)
    greeks = black_scholes(
        spot, float(leg["strike"]), max(dte, 1) / 365, 0.03, 0.012, iv, leg["option_type"]
    )
    spread = max(0.02, greeks.price * 0.035)
    return pd.Series(
        {
            **leg.to_dict(),
            "underlying_price": spot,
            "implied_volatility": iv,
            "bid": max(greeks.price - spread / 2, 0.01),
            "ask": greeks.price + spread / 2,
            "delta": greeks.delta,
            "vega": greeks.vega,
        }
    )


def _open_position(
    day_chain: pd.DataFrame,
    config: BacktestConfig,
    signal_date: pd.Timestamp,
    signal: str,
) -> tuple[Position | None, list[dict[str, Any]]]:
    legs = select_legs(day_chain, config.strategy)
    per_contract: list[dict[str, Any]] = []
    for _, leg in legs.iterrows():
        quantity = int(leg["quantity"])
        price = _execution_price(leg, quantity, True, config.risk.slippage_bps)
        per_contract.append(
            {
                "option_type": leg["option_type"],
                "strike": float(leg["strike"]),
                "expiry": pd.Timestamp(leg["expiry"]).date().isoformat(),
                "quantity": quantity,
                "entry_price": price,
                "price": price,
            }
        )
    spot = float(day_chain["underlying_price"].iloc[0])
    margin_per_contract = reg_t_margin(config.strategy.name, per_contract, spot)
    entry_cashflow_per_contract = sum(
        -int(leg["quantity"]) * float(leg["entry_price"]) * CONTRACT_MULTIPLIER
        for leg in per_contract
    )
    if config.strategy.name in {
        StrategyName.SHORT_STRADDLE,
        StrategyName.SHORT_STRANGLE,
    }:
        risk_per_contract = margin_per_contract * 0.25
    else:
        risk_per_contract = max(abs(entry_cashflow_per_contract), margin_per_contract)
    contracts = position_size(config.risk, risk_per_contract, margin_per_contract)
    if contracts == 0:
        return None, []

    legs = legs.copy()
    legs["quantity"] *= contracts
    records = []
    cashflow = 0.0
    commission = 0.0
    for leg in per_contract:
        quantity = int(leg["quantity"]) * contracts
        price = float(leg["entry_price"])
        cashflow += -quantity * price * CONTRACT_MULTIPLIER
        commission += abs(quantity) * config.risk.commission_per_contract
        records.append({**leg, "quantity": quantity})
    cashflow -= commission
    position = Position(
        opened=pd.Timestamp(day_chain["date"].iloc[0]),
        signal_date=signal_date,
        signal=signal,
        legs=legs,
        entry_cashflow=cashflow,
        entry_cost_basis=max(abs(cashflow), 1.0),
        commission=commission,
        margin=margin_per_contract * contracts,
        previous_spot=spot,
    )
    return position, records


def _mark_position(
    position: Position, day_chain: pd.DataFrame, config: BacktestConfig
) -> tuple[float, float, float, float, list[pd.Series]]:
    exit_cashflow = 0.0
    delta = 0.0
    vega = 0.0
    quotes = []
    for _, leg in position.legs.iterrows():
        quote = _current_quote(leg, day_chain)
        quotes.append(quote)
        quantity = int(leg["quantity"])
        price = _execution_price(quote, quantity, False, config.risk.slippage_bps)
        exit_cashflow += quantity * price * CONTRACT_MULTIPLIER
        delta += quantity * float(quote["delta"]) * CONTRACT_MULTIPLIER
        vega += quantity * float(quote["vega"]) * CONTRACT_MULTIPLIER
    pnl = position.entry_cashflow + exit_cashflow + position.hedge_pnl
    return pnl, delta, vega, exit_cashflow, quotes


def _should_exit(
    position: Position,
    day: pd.Timestamp,
    pnl: float,
    factor: pd.Series,
    config: BacktestConfig,
) -> str | None:
    holding = len(pd.bdate_range(position.opened, day)) - 1
    dte = (pd.Timestamp(position.legs["expiry"].iloc[0]) - day).days
    normalized = pnl / position.entry_cost_basis
    if normalized <= -config.risk.stop_loss:
        return "stop_loss"
    if normalized >= config.risk.profit_target:
        return "profit_target"
    if dte <= config.strategy.min_exit_dte:
        return "dte_exit"
    if holding >= config.strategy.max_holding_days:
        return "max_holding"
    percentile = factor["iv_percentile_60"]
    if pd.notna(percentile) and config.signal.exit_low <= percentile <= config.signal.exit_high:
        return "mean_reversion"
    return None


def _serialize_factor(row: pd.Series) -> dict[str, Any]:
    result: dict[str, Any] = {"date": pd.Timestamp(row["date"]).date().isoformat()}
    for key in (
        "underlying_price",
        "implied_volatility",
        "rv20",
        "iv_percentile_20",
        "iv_percentile_60",
        "iv_rv_zscore",
    ):
        value = row[key]
        result[key] = None if pd.isna(value) else float(value)
    result["signal"] = row["signal"]
    return result


def run_backtest(chain: pd.DataFrame, config: BacktestConfig) -> BacktestResult:
    chain = validate_option_chain(chain)
    start = pd.Timestamp(config.start_date)
    end = pd.Timestamp(config.end_date)
    chain = chain[(chain["date"] >= start) & (chain["date"] <= end)].copy()
    if chain.empty:
        raise ValueError("no quotes in configured date range")

    daily_market = (
        chain.groupby("date", as_index=False)
        .agg(
            underlying_price=("underlying_price", "first"),
            implied_volatility=("implied_volatility", "median"),
        )
    )
    factors = compute_volatility_factors(daily_market)
    factors["signal"] = factors.apply(lambda row: _signal(row, config), axis=1)
    factor_by_date = factors.set_index("date")

    capital = config.risk.initial_capital
    realized_pnl = 0.0
    position: Position | None = None
    trades: list[dict[str, Any]] = []
    leg_records: list[dict[str, Any]] = []
    equity_records: list[dict[str, Any]] = []
    exposures: list[dict[str, Any]] = []

    dates = sorted(chain["date"].unique())
    for index, raw_day in enumerate(dates):
        day = pd.Timestamp(raw_day)
        day_chain = chain[chain["date"] == day]
        factor = factor_by_date.loc[day]
        spot = float(day_chain["underlying_price"].iloc[0])

        if position is not None and config.strategy.delta_hedge:
            position.hedge_pnl += position.hedge_shares * (spot - position.previous_spot)
            position.previous_spot = spot

        unrealized = 0.0
        delta = 0.0
        vega = 0.0
        exit_cashflow = 0.0
        if position is not None:
            unrealized, delta, vega, exit_cashflow, _ = _mark_position(position, day_chain, config)
            reason = _should_exit(position, day, unrealized, factor, config)
            if reason:
                close_commission = (
                    position.legs["quantity"].abs().sum()
                    * config.risk.commission_per_contract
                )
                pnl = unrealized - close_commission
                realized_pnl += pnl
                trades.append(
                    {
                        "date": day.date().isoformat(),
                        "event": "close",
                        "strategy": config.strategy.name.value,
                        "reason": reason,
                        "pnl": pnl,
                        "signal_date": position.signal_date.date().isoformat(),
                    }
                )
                position = None
                unrealized = 0.0
                delta = 0.0
                vega = 0.0

        if position is None and index > 0:
            signal_row = factors.iloc[index - 1]
            signal = str(signal_row["signal"])
            if _strategy_accepts_signal(config.strategy.name, signal):
                signal_date = pd.Timestamp(signal_row["date"])
                opened, opened_legs = _open_position(day_chain, config, signal_date, signal)
                if opened is not None:
                    position = opened
                    trade_index = len(trades)
                    for leg in opened_legs:
                        leg_records.append({"trade_index": trade_index, **leg})
                    trades.append(
                        {
                            "date": day.date().isoformat(),
                            "event": "open",
                            "strategy": config.strategy.name.value,
                            "signal": signal,
                            "signal_date": signal_date.date().isoformat(),
                            "pnl": 0.0,
                        }
                    )
                    unrealized, delta, vega, exit_cashflow, _ = _mark_position(
                        position, day_chain, config
                    )

        if position is not None and config.strategy.delta_hedge:
            position.hedge_shares = -delta
            net_delta = 0.0
        else:
            net_delta = delta

        equity = capital + realized_pnl + unrealized
        equity_records.append({"date": day.date().isoformat(), "equity": equity})
        exposures.append(
            {
                "date": day.date().isoformat(),
                "delta": net_delta,
                "vega": vega,
                "margin_used": position.margin if position is not None else 0.0,
                "open_positions": int(position is not None),
            }
        )

    closed = pd.DataFrame([trade for trade in trades if trade["event"] == "close"])
    equity_series = pd.Series(
        [row["equity"] for row in equity_records],
        index=pd.to_datetime([row["date"] for row in equity_records]),
    )
    metrics = calculate_performance(equity_series, closed)
    peak = equity_series.cummax()
    for record, drawdown in zip(equity_records, equity_series / peak - 1, strict=True):
        record["drawdown"] = float(drawdown)

    warnings = [
        "Synthetic option-chain data; results are not live trading performance.",
        "Black-Scholes approximation does not model American early exercise.",
    ]
    return BacktestResult(
        run_id=uuid4().hex[:12],
        status="completed",
        data_source=config.dataset,
        config=config,
        metrics=metrics,
        equity_curve=equity_records,
        factors=[_serialize_factor(row) for _, row in factors.iterrows()],
        exposures=exposures,
        trades=trades,
        legs=leg_records,
        warnings=warnings,
    )
