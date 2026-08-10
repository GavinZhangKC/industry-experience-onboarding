import json
from types import SimpleNamespace

from app.config import Settings
from lambda_handlers import health


def _event(method: str = "GET"):
    return {
        "rawPath": "/health",
        "headers": {},
        "requestContext": {
            "requestId": "health-function-url-id",
            "http": {"method": method, "path": "/health"},
        },
    }


def test_health_handler_matches_the_fastapi_payload(monkeypatch):
    settings = Settings(_env_file=None)
    store = SimpleNamespace(busy_areas=[{}], quiet_spaces=[{}, {}])
    monkeypatch.setattr(health, "get_settings", lambda: settings)
    monkeypatch.setattr(health, "get_configured_data_store", lambda _: store)

    response = health.handler(_event(), context=None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "status": "ok",
        "maps_provider": "mock",
        "busy_areas": 1,
        "quiet_spaces": 2,
    }
    assert response["headers"]["X-Request-ID"] == "health-function-url-id"


def test_health_handler_rejects_non_get_requests():
    response = health.handler(_event(method="POST"), context=None)

    assert response["statusCode"] == 405
    assert response["headers"]["Allow"] == "GET"
