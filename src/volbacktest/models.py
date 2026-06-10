from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class OptionType(StrEnum):
    CALL = "call"
    PUT = "put"


class StrategyName(StrEnum):
    LONG_STRADDLE = "long_straddle"
    SHORT_STRADDLE = "short_straddle"
    LONG_STRANGLE = "long_strangle"
    SHORT_STRANGLE = "short_strangle"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"


class OptionQuote(BaseModel):
    date: date
    expiry: date
    option_type: OptionType
    strike: float = Field(gt=0)
    bid: float = Field(ge=0)
    ask: float = Field(gt=0)
    implied_volatility: float = Field(gt=0, le=5)
    underlying_price: float = Field(gt=0)
    delta: float | None = None
    gamma: float | None = None
    vega: float | None = None
    theta: float | None = None

    @model_validator(mode="after")
    def validate_market(self) -> OptionQuote:
        if self.expiry <= self.date:
            raise ValueError("expiry must be after date")
        if self.bid > self.ask:
            raise ValueError("bid cannot exceed ask")
        return self


class OptionChain(BaseModel):
    quotes: list[OptionQuote]
    source: str = "synthetic"


class SignalConfig(BaseModel):
    low_percentile: float = Field(default=20, ge=0, le=100)
    high_percentile: float = Field(default=80, ge=0, le=100)
    zscore_threshold: float = Field(default=1.0, ge=0)
    exit_low: float = Field(default=40, ge=0, le=100)
    exit_high: float = Field(default=60, ge=0, le=100)


class RiskConfig(BaseModel):
    initial_capital: float = Field(default=250_000, gt=0)
    risk_per_trade: float = Field(default=0.02, gt=0, le=1)
    max_margin_fraction: float = Field(default=0.40, gt=0, le=1)
    max_positions: int = Field(default=5, ge=1)
    stop_loss: float = Field(default=0.20, gt=0)
    profit_target: float = Field(default=0.25, gt=0)
    commission_per_contract: float = Field(default=0.65, ge=0)
    slippage_bps: float = Field(default=1.0, ge=0)


class StrategySpec(BaseModel):
    name: StrategyName = StrategyName.SHORT_STRANGLE
    target_dte: int = Field(default=30, ge=7, le=120)
    min_exit_dte: int = Field(default=5, ge=1)
    max_holding_days: int = Field(default=10, ge=1)
    delta_hedge: bool = True


class BacktestConfig(BaseModel):
    dataset: str = "synthetic"
    start_date: date = date(2020, 1, 2)
    end_date: date = date(2024, 12, 31)
    seed: int = 42
    strategy: StrategySpec = Field(default_factory=StrategySpec)
    signal: SignalConfig = Field(default_factory=SignalConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)

    @model_validator(mode="after")
    def validate_dates(self) -> BacktestConfig:
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class BacktestResult(BaseModel):
    run_id: str
    status: str
    data_source: str
    config: BacktestConfig
    metrics: dict[str, float]
    equity_curve: list[dict[str, Any]]
    factors: list[dict[str, Any]]
    exposures: list[dict[str, Any]]
    trades: list[dict[str, Any]]
    legs: list[dict[str, Any]]
    warnings: list[str] = Field(default_factory=list)

