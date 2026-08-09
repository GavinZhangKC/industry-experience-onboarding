from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.deps import maps_dep, settings_dep, store_dep
from app.clients.maps_client import RawRoute
from app.config import Settings
from app.lib.geo import encode_polyline
from app.main import create_app


VALID_REQUEST = {
    "origin": {"lat": -37.8113, "lng": 144.9541},
    "destination": {"lat": -37.8140, "lng": 144.9737},
    "alternatives": 2,
}


class FakeMapsClient:
    async def walking_routes(self, origin, destination, alternatives):
        direct = encode_polyline([origin, destination])
        via_point = encode_polyline([origin, (-37.8070, 144.9630), destination])
        return [
            RawRoute(distance_m=1800, duration_s=1300, polyline=direct),
            RawRoute(distance_m=2200, duration_s=1600, polyline=via_point),
        ][:alternatives]


@pytest.fixture
def client():
    app = create_app()
    app.dependency_overrides[settings_dep] = lambda: Settings(_env_file=None)
    app.dependency_overrides[maps_dep] = lambda: FakeMapsClient()
    app.dependency_overrides[store_dep] = lambda: SimpleNamespace(busy_areas=[])

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_routes_returns_at_least_two_complete_routes(client: TestClient):
    response = client.post("/api/v1/routes", json=VALID_REQUEST)

    assert response.status_code == 200
    body = response.json()
    assert "generated_at" in body
    assert len(body["routes"]) >= 2
    for route in body["routes"]:
        assert {
            "id",
            "label",
            "distance_m",
            "duration_s",
            "polyline",
            "sensory",
        } <= route.keys()
        assert route["distance_m"] > 0
        assert route["duration_s"] > 0
        assert route["polyline"]


def test_create_routes_rejects_same_origin_and_destination(client: TestClient):
    payload = {**VALID_REQUEST, "destination": VALID_REQUEST["origin"]}

    response = client.post("/api/v1/routes", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_create_routes_rejects_invalid_latitude(client: TestClient):
    payload = {**VALID_REQUEST, "origin": {"lat": -91, "lng": 144.9541}}

    response = client.post("/api/v1/routes", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_create_routes_rejects_fewer_than_two_alternatives(client: TestClient):
    payload = {**VALID_REQUEST, "alternatives": 1}

    response = client.post("/api/v1/routes", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_create_routes_rejects_a_point_outside_the_service_area(client: TestClient):
    payload = {**VALID_REQUEST, "origin": {"lat": -38.5, "lng": 144.9541}}

    response = client.post("/api/v1/routes", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "out_of_service_area"
