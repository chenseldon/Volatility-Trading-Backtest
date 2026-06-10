from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from apps.api.main import create_app
from volbacktest.data import generate_synthetic_chain
from volbacktest.service import BacktestService


def test_api_catalog_and_backtest_share_service_contract(tmp_path: Path) -> None:
    client = TestClient(create_app(BacktestService(output_dir=tmp_path)))

    catalog = client.get("/api/v1/catalog")
    assert catalog.status_code == 200
    assert "short_strangle" in catalog.json()["strategies"]

    response = client.post(
        "/api/v1/backtests",
        json={
            "dataset": "synthetic",
            "start_date": "2024-01-02",
            "end_date": "2024-06-30",
            "seed": 3,
            "signal": {
                "low_percentile": 40,
                "high_percentile": 60,
                "zscore_threshold": 0,
                "exit_low": 40,
                "exit_high": 60
            }
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["data_source"] == "synthetic"
    assert client.get(f"/api/v1/backtests/{body['run_id']}").status_code == 200
    assert client.get("/api/v1/backtests").json()[0]["run_id"] == body["run_id"]


def test_api_returns_structured_validation_errors(tmp_path: Path) -> None:
    client = TestClient(create_app(BacktestService(output_dir=tmp_path)))

    response = client.post(
        "/api/v1/backtests",
        json={"start_date": "2025-01-02", "end_date": "2024-01-02"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error"


def test_api_uploads_a_valid_csv_for_later_backtests(tmp_path: Path) -> None:
    client = TestClient(create_app(BacktestService(output_dir=tmp_path)))
    chain = generate_synthetic_chain(periods=80, seed=17)
    dates = sorted(chain["date"].unique())

    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("chain.csv", chain.to_csv(index=False), "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["rows"] == len(chain)
    assert body["dataset"].startswith("upload:")

    run = client.post(
        "/api/v1/backtests",
        json={
            "dataset": body["dataset"],
            "start_date": pd.Timestamp(dates[0]).date().isoformat(),
            "end_date": pd.Timestamp(dates[-1]).date().isoformat(),
            "signal": {
                "low_percentile": 40,
                "high_percentile": 60,
                "zscore_threshold": 0,
                "exit_low": 40,
                "exit_high": 60,
            },
        },
    )

    assert run.status_code == 200
    assert run.json()["data_source"] == body["dataset"]


def test_api_returns_structured_error_for_unknown_uploaded_dataset(tmp_path: Path) -> None:
    client = TestClient(create_app(BacktestService(output_dir=tmp_path)))

    response = client.post(
        "/api/v1/backtests",
        json={
            "dataset": f"upload:{'a' * 32}",
            "start_date": "2025-01-02",
            "end_date": "2025-02-01",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "backtest_failed"
