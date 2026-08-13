from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import store_dep
from app.main import create_app


def test_predictive_alerts_endpoint_returns_trending_areas():
    app = create_app()
    app.dependency_overrides[store_dep] = lambda: SimpleNamespace(
        trending_areas=[
            {
                "id": "sensor-1",
                "name": "Swanston Street",
                "lat": -37.81,
                "lng": 144.96,
                "latest": 90,
                "prev": 60,
                "percent_increase": 50.0,
            }
        ]
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/predictive-alerts")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["alerts"][0]["id"] == "sensor-1"
    assert response.json()["alerts"][0]["percent_increase"] == 50.0
