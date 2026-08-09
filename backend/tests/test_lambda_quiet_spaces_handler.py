import json
from types import SimpleNamespace

from app.config import Settings
from app.errors import OutOfServiceArea
from app.schemas import QuietSpace, QuietSpaceResponse
from lambda_handlers import quiet_spaces


def _event(
    *,
    method: str = "GET",
    path: str = "/api/v1/quiet-spaces",
    query=None,
):
    return {
        "version": "2.0",
        "rawPath": path,
        "headers": {},
        "queryStringParameters": query
        if query is not None
        else {"lat": "-37.8140", "lng": "144.9700"},
        "requestContext": {
            "requestId": "quiet-function-url-id",
            "http": {"method": method, "path": path},
        },
        "body": None,
        "isBase64Encoded": False,
    }


def _quiet_response(radius_m: int = 500) -> QuietSpaceResponse:
    return QuietSpaceResponse(
        quiet_spaces=[
            QuietSpace(
                id="library",
                name="Nearby Library",
                type="library",
                category="indoor",
                lat=-37.8140,
                lng=144.9705,
                distance_m=44,
                description="A calm library.",
            )
        ],
        radius_m=radius_m,
    )


def _replace_dependencies(monkeypatch, find_quiet_spaces):
    settings = Settings(_env_file=None)
    store = SimpleNamespace(quiet_spaces=[])
    monkeypatch.setattr(quiet_spaces, "get_settings", lambda: settings)
    monkeypatch.setattr(
        quiet_spaces, "get_configured_data_store", lambda actual: store
    )
    monkeypatch.setattr(quiet_spaces, "find_quiet_spaces", find_quiet_spaces)
    return settings, store


def test_quiet_space_handler_returns_function_url_response(monkeypatch):
    captured = {}

    def fake_find(lat, lng, *, radius_m, limit, category, store, settings):
        captured.update(
            lat=lat,
            lng=lng,
            radius_m=radius_m,
            limit=limit,
            category=category,
            store=store,
            settings=settings,
        )
        return _quiet_response(radius_m)

    settings, store = _replace_dependencies(monkeypatch, fake_find)

    response = quiet_spaces.handler(_event(), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"
    assert response["headers"]["X-Request-ID"] == "quiet-function-url-id"
    assert body["quiet_spaces"][0]["id"] == "library"
    assert captured == {
        "lat": -37.814,
        "lng": 144.97,
        "radius_m": 500,
        "limit": 5,
        "category": None,
        "store": store,
        "settings": settings,
    }


def test_quiet_space_handler_parses_optional_query_values(monkeypatch):
    captured = {}

    def fake_find(lat, lng, *, radius_m, limit, category, store, settings):
        captured.update(radius_m=radius_m, limit=limit, category=category)
        return _quiet_response(radius_m)

    _replace_dependencies(monkeypatch, fake_find)
    event = _event(
        query={
            "lat": "-37.8140",
            "lng": "144.9700",
            "radius_m": "1000",
            "limit": "10",
            "category": "indoor",
        }
    )

    response = quiet_spaces.handler(event, context=None)

    assert response["statusCode"] == 200
    assert captured == {"radius_m": 1000, "limit": 10, "category": "indoor"}


def test_quiet_space_handler_rejects_invalid_query():
    response = quiet_spaces.handler(
        _event(query={"lat": "not-a-number", "lng": "144.97"}),
        context=None,
    )
    body = json.loads(response["body"])

    assert response["statusCode"] == 422
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["details"]["fields"][0]["field"] == "lat"


def test_quiet_space_handler_rejects_missing_query_parameters():
    response = quiet_spaces.handler(_event(query={}), context=None)

    assert response["statusCode"] == 422
    assert json.loads(response["body"])["error"]["code"] == "invalid_request"


def test_quiet_space_handler_rejects_unsupported_method():
    response = quiet_spaces.handler(_event(method="POST"), context=None)

    assert response["statusCode"] == 405
    assert response["headers"]["Allow"] == "GET"


def test_quiet_space_handler_converts_service_error(monkeypatch):
    def fake_find(*args, **kwargs):
        raise OutOfServiceArea()

    _replace_dependencies(monkeypatch, fake_find)

    response = quiet_spaces.handler(_event(), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 422
    assert body["error"]["code"] == "out_of_service_area"
    assert body["error"]["request_id"] == "quiet-function-url-id"
