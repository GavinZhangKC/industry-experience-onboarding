import base64
import json
from types import SimpleNamespace

from app.config import Settings
from app.errors import NoRoutesFound
from app.schemas import RouteOption, RouteResponse, SensoryResult
from lambda_handlers import routes


VALID_BODY = {
    "origin": {"lat": -37.8113, "lng": 144.9541},
    "destination": {"lat": -37.8140, "lng": 144.9737},
    "alternatives": 2,
}


def _event(
    *,
    method: str = "POST",
    path: str = "/api/v1/routes",
    body=VALID_BODY,
    encoded: bool = False,
):
    raw_body = body if isinstance(body, str) else json.dumps(body)
    if encoded:
        raw_body = base64.b64encode(raw_body.encode("utf-8")).decode("ascii")
    return {
        "version": "2.0",
        "rawPath": path,
        "headers": {"content-type": "application/json"},
        "requestContext": {
            "requestId": "function-url-request-id",
            "http": {"method": method, "path": path},
        },
        "body": raw_body,
        "isBase64Encoded": encoded,
    }


def _route_response() -> RouteResponse:
    sensory = SensoryResult(
        score=0,
        level="low",
        explanation="This route stays clear of the busy areas we track.",
        factors=[],
    )
    return RouteResponse(
        routes=[
            RouteOption(
                id="route-0",
                label="Route A",
                distance_m=1800,
                duration_s=1300,
                polyline="encoded-route-a",
                sensory=sensory,
            ),
            RouteOption(
                id="route-1",
                label="Route B",
                distance_m=2200,
                duration_s=1600,
                polyline="encoded-route-b",
                sensory=sensory,
            ),
        ],
        generated_at="2026-08-08T00:00:00+00:00",
    )


def _replace_dependencies(monkeypatch, plan_routes):
    settings = Settings(_env_file=None)
    maps_client = object()
    store = SimpleNamespace(busy_areas=[])
    monkeypatch.setattr(routes, "get_settings", lambda: settings)
    monkeypatch.setattr(routes, "get_maps_client", lambda actual: maps_client)
    monkeypatch.setattr(routes, "get_data_store", lambda data_dir: store)
    monkeypatch.setattr(routes, "plan_routes", plan_routes)
    return settings, maps_client, store


def test_route_handler_returns_function_url_response(monkeypatch):
    captured = {}

    async def fake_plan_routes(request, *, maps_client, store, settings):
        captured.update(
            request=request,
            maps_client=maps_client,
            store=store,
            settings=settings,
        )
        return _route_response()

    settings, maps_client, store = _replace_dependencies(
        monkeypatch, fake_plan_routes
    )

    response = routes.handler(_event(), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"
    assert response["headers"]["X-Request-ID"] == "function-url-request-id"
    assert response["isBase64Encoded"] is False
    assert len(body["routes"]) == 2
    assert captured["request"].alternatives == 2
    assert captured["maps_client"] is maps_client
    assert captured["store"] is store
    assert captured["settings"] is settings


def test_route_handler_accepts_base64_encoded_json(monkeypatch):
    async def fake_plan_routes(*args, **kwargs):
        return _route_response()

    _replace_dependencies(monkeypatch, fake_plan_routes)

    response = routes.handler(_event(encoded=True), context=None)

    assert response["statusCode"] == 200


def test_route_handler_rejects_malformed_json():
    response = routes.handler(_event(body="{not-json"), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 422
    assert body["error"]["code"] == "invalid_request"


def test_route_handler_reuses_route_request_validation():
    invalid = {**VALID_BODY, "alternatives": 1}

    response = routes.handler(_event(body=invalid), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 422
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["details"]["fields"][0]["field"] == "alternatives"


def test_route_handler_rejects_unsupported_path():
    response = routes.handler(_event(path="/api/v1/quiet-spaces"), context=None)

    assert response["statusCode"] == 404
    assert json.loads(response["body"])["error"]["code"] == "not_found"


def test_route_handler_rejects_unsupported_method():
    response = routes.handler(_event(method="GET"), context=None)

    assert response["statusCode"] == 405
    assert response["headers"]["Allow"] == "POST"


def test_route_handler_converts_service_error(monkeypatch):
    async def fake_plan_routes(*args, **kwargs):
        raise NoRoutesFound()

    _replace_dependencies(monkeypatch, fake_plan_routes)

    response = routes.handler(_event(), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 404
    assert body["error"] == {
        "code": "no_routes_found",
        "message": "No walking routes were found between those two points.",
        "request_id": "function-url-request-id",
    }


def test_route_handler_hides_unexpected_error_details(monkeypatch):
    async def fake_plan_routes(*args, **kwargs):
        raise RuntimeError("secret implementation detail")

    _replace_dependencies(monkeypatch, fake_plan_routes)

    response = routes.handler(_event(), context=None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert body["error"]["code"] == "internal_error"
    assert "secret implementation detail" not in response["body"]
