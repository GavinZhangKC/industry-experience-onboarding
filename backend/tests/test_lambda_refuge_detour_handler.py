import json
from types import SimpleNamespace

from app.config import Settings
from app.schemas import RefugeDetourResponse, RefugeLeg, SensoryResult
from lambda_handlers import refuge_detour


VALID_BODY = {
    "current": {"lat": -37.8113, "lng": 144.9541},
    "refuge": {"lat": -37.8140, "lng": 144.9737},
    "destination": {"lat": -37.8102, "lng": 144.9628},
}


def _event(method: str = "POST", body=VALID_BODY):
    return {
        "rawPath": "/api/v1/refuge-detour",
        "headers": {},
        "requestContext": {
            "requestId": "detour-function-url-id",
            "http": {"method": method, "path": "/api/v1/refuge-detour"},
        },
        "body": body if isinstance(body, str) else json.dumps(body),
        "isBase64Encoded": False,
    }


def _response() -> RefugeDetourResponse:
    sensory = SensoryResult(score=0, level="low", explanation="Calm.", factors=[])
    leg = RefugeLeg(
        name="To refuge",
        distance_m=200,
        duration_s=150,
        polyline="encoded-polyline",
        sensory=sensory,
    )
    return RefugeDetourResponse(
        legs=[leg, leg.model_copy(update={"name": "Refuge to destination"})],
        total_distance_m=400,
        total_duration_s=300,
        generated_at="2026-08-10T00:00:00+00:00",
    )


def test_refuge_detour_handler_delegates_to_the_service(monkeypatch):
    captured = {}
    settings = Settings(_env_file=None)
    maps_client = object()
    store = SimpleNamespace(busy_areas=[])

    async def fake_plan(request, *, maps_client: object, store: object, settings: Settings):
        captured.update(request=request, maps_client=maps_client, store=store, settings=settings)
        return _response()

    monkeypatch.setattr(refuge_detour, "get_settings", lambda: settings)
    monkeypatch.setattr(refuge_detour, "get_maps_client", lambda _: maps_client)
    monkeypatch.setattr(refuge_detour, "get_configured_data_store", lambda _: store)
    monkeypatch.setattr(refuge_detour, "plan_refuge_detour", fake_plan)

    response = refuge_detour.handler(_event(), context=None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["total_distance_m"] == 400
    assert captured["request"].refuge.lat == -37.814
    assert captured["maps_client"] is maps_client
    assert captured["store"] is store


def test_refuge_detour_handler_rejects_invalid_json():
    response = refuge_detour.handler(_event(body="not-json"), context=None)

    assert response["statusCode"] == 422
    assert json.loads(response["body"])["error"]["code"] == "invalid_request"
