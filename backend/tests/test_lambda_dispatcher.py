import json

from lambda_handlers import handler as dispatcher


def _event(path: str):
    return {
        "rawPath": path,
        "headers": {},
        "requestContext": {
            "requestId": "dispatcher-request-id",
            "http": {"method": "GET", "path": path},
        },
    }


def test_dispatcher_sends_routes_path_to_route_handler(monkeypatch):
    expected = {"statusCode": 200, "body": "routes"}
    monkeypatch.setattr(
        dispatcher.routes, "handler", lambda event, context: expected
    )

    assert dispatcher.handler(_event("/api/v1/routes"), None) is expected


def test_dispatcher_sends_health_path_to_health_handler(monkeypatch):
    expected = {"statusCode": 200, "body": "health"}
    monkeypatch.setattr(dispatcher.health, "handler", lambda event, context: expected)

    assert dispatcher.handler(_event("/health"), None) is expected


def test_dispatcher_sends_quiet_path_to_quiet_handler(monkeypatch):
    expected = {"statusCode": 200, "body": "quiet"}
    monkeypatch.setattr(
        dispatcher.quiet_spaces, "handler", lambda event, context: expected
    )

    assert dispatcher.handler(_event("/api/v1/quiet-spaces"), None) is expected


def test_dispatcher_sends_refuge_detour_path_to_handler(monkeypatch):
    expected = {"statusCode": 200, "body": "refuge-detour"}
    monkeypatch.setattr(
        dispatcher.refuge_detour, "handler", lambda event, context: expected
    )

    assert dispatcher.handler(_event("/api/v1/refuge-detour"), None) is expected


def test_dispatcher_returns_enveloped_404_for_unknown_path():
    response = dispatcher.handler(_event("/unknown"), None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 404
    assert body["error"]["code"] == "not_found"
    assert body["error"]["request_id"] == "dispatcher-request-id"
