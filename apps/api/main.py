from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from volbacktest.data import DataValidationError, validate_option_chain
from volbacktest.models import BacktestConfig, StrategyName
from volbacktest.service import BacktestService

UPLOAD_FILE = File(...)


class SweepRequest(BaseModel):
    config: BacktestConfig
    parameter_grid: dict[str, list[Any]]


def create_app(service: BacktestService | None = None) -> FastAPI:
    app = FastAPI(title="Volatility Trading Backtest API", version="1.0.0")
    engine = service or BacktestService()

    @app.get("/api/v1/catalog")
    def catalog() -> dict[str, Any]:
        return {
            "strategies": [strategy.value for strategy in StrategyName],
            "datasets": ["synthetic", "CSV upload"],
            "artifacts": [
                "result.json",
                "report.md",
                "trades.csv",
                "legs.csv",
                "equity.png",
                "drawdown.png",
            ],
        }

    @app.post("/api/v1/datasets/validate")
    async def validate_dataset(file: UploadFile = UPLOAD_FILE) -> dict[str, Any]:
        import pandas as pd

        try:
            frame = pd.read_csv(file.file)
            validated = validate_option_chain(frame)
        except (DataValidationError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "invalid_option_chain", "message": str(exc)},
            ) from exc
        return {"valid": True, "rows": len(validated), "columns": list(validated.columns)}

    @app.post("/api/v1/backtests")
    def run_backtest(config: BacktestConfig) -> dict[str, Any]:
        return engine.run(config).model_dump(mode="json")

    @app.post("/api/v1/sweeps")
    def run_sweep(request: SweepRequest) -> list[dict[str, Any]]:
        return engine.sweep(request.config, request.parameter_grid)

    @app.get("/api/v1/backtests")
    def list_backtests() -> list[dict[str, Any]]:
        return engine.list_runs()

    @app.get("/api/v1/backtests/{run_id}")
    def get_backtest(run_id: str) -> dict[str, Any]:
        try:
            return engine.get(run_id).model_dump(mode="json")
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

    @app.get("/api/v1/artifacts/{run_id}/{name}")
    def get_artifact(run_id: str, name: str) -> FileResponse:
        try:
            return FileResponse(engine.artifact(run_id, name), filename=name)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="artifact not found") from exc

    return app


app = create_app()
