from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.deps import settings_dep, store_dep
from app.config import Settings
from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.dependency_overrides[settings_dep] = lambda: Settings(_env_file=None)
    app.dependency_overrides[store_dep] = lambda: SimpleNamespace(
        quiet_spaces=[
            {
                "id": "library",
                "name": "Nearby Library",
                "type": "library",
                "lat": -37.8140,
                "lng": 144.9705,
            }
        ]
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_quiet_spaces_endpoint_returns_nearby_results(client: TestClient):
    response = client.get(
        "/api/v1/quiet-spaces",
        params={"lat": -37.8140, "lng": 144.9700, "radius_m": 500},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["radius_m"] == 500
    assert body["quiet_spaces"][0]["id"] == "library"


@pytest.mark.parametrize(
    "params",
    [
        {"lng": 144.97},
        {"lat": -91, "lng": 144.97},
        {"lat": -37.81, "lng": 144.97, "radius_m": 50},
        {"lat": -37.81, "lng": 144.97, "limit": 21},
    ],
)
def test_quiet_spaces_endpoint_rejects_invalid_query(client: TestClient, params):
    response = client.get("/api/v1/quiet-spaces", params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
