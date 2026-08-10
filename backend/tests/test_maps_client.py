import asyncio

import pytest

from app.clients import maps_client
from app.config import Settings
from app.errors import UpstreamError
from app.lib.geo import encode_polyline


class FakeResponse:
    status_code = 200

    def __init__(self, payload=None, error: Exception | None = None):
        self._payload = payload
        self._error = error

    def json(self):
        if self._error:
            raise self._error
        return self._payload


class FakeAsyncClient:
    def __init__(self, response: FakeResponse):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, *args, **kwargs):
        return self._response


def _client(response: FakeResponse, monkeypatch):
    monkeypatch.setattr(
        maps_client.httpx,
        "AsyncClient",
        lambda **_: FakeAsyncClient(response),
    )
    return maps_client.GoogleMapsClient(
        Settings(google_maps_api_key="test-key", _env_file=None)
    )


def test_google_client_rejects_a_route_without_a_usable_polyline(monkeypatch):
    response = FakeResponse(
        {"routes": [{"distanceMeters": 400, "duration": "300s", "polyline": {}}]}
    )

    with pytest.raises(UpstreamError):
        asyncio.run(_client(response, monkeypatch).walking_routes((1, 2), (3, 4), 2))


def test_google_client_rejects_a_malformed_polyline(monkeypatch):
    response = FakeResponse(
        {
            "routes": [
                {
                    "distanceMeters": 400,
                    "duration": "300s",
                    "polyline": {"encodedPolyline": "abc"},
                }
            ]
        }
    )

    with pytest.raises(UpstreamError):
        asyncio.run(_client(response, monkeypatch).walking_routes((1, 2), (3, 4), 2))


def test_google_client_rejects_invalid_json(monkeypatch):
    with pytest.raises(UpstreamError):
        asyncio.run(
            _client(FakeResponse(error=ValueError("bad json")), monkeypatch).walking_routes(
                (1, 2), (3, 4), 2
            )
        )


def test_google_client_accepts_a_complete_route(monkeypatch):
    polyline = encode_polyline([(-37.81, 144.96), (-37.82, 144.97)])
    response = FakeResponse(
        {
            "routes": [
                {
                    "distanceMeters": 400,
                    "duration": "300s",
                    "polyline": {"encodedPolyline": polyline},
                }
            ]
        }
    )

    routes = asyncio.run(_client(response, monkeypatch).walking_routes((1, 2), (3, 4), 2))

    assert routes[0].distance_m == 400
    assert routes[0].duration_s == 300
