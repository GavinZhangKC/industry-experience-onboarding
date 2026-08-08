"""AWS Lambda Function URL adapter for BE-F1 + BE-F2 routes."""

import asyncio
import logging
from typing import Any

from pydantic import ValidationError

from app.clients.maps_client import get_maps_client
from app.config import get_settings
from app.errors import AppError
from app.lib.data_store import get_configured_data_store
from app.schemas import RouteRequest
from app.services.route_service import plan_routes
from lambda_handlers.common import (
    MalformedBody,
    app_error_response,
    error_response,
    get_method,
    get_path,
    get_request_id,
    json_response,
    parse_json_body,
    validation_error_response,
)

logger = logging.getLogger(__name__)

ROUTES_PATH = "/api/v1/routes"


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle POST /api/v1/routes from a Lambda Function URL event."""
    request_id = get_request_id(event, context)
    path = get_path(event)
    method = get_method(event)

    if path != ROUTES_PATH:
        return error_response(
            404,
            "not_found",
            "The requested endpoint was not found.",
            request_id=request_id,
        )
    if method != "POST":
        return error_response(
            405,
            "method_not_allowed",
            "This endpoint only accepts POST requests.",
            request_id=request_id,
            headers={"Allow": "POST"},
        )

    try:
        payload = parse_json_body(event)
        request = RouteRequest.model_validate(payload)
        settings = get_settings()
        result = asyncio.run(
            plan_routes(
                request,
                maps_client=get_maps_client(settings),
                store=get_configured_data_store(settings),
                settings=settings,
            )
        )
        return json_response(
            200,
            result.model_dump(mode="json"),
            request_id=request_id,
        )
    except MalformedBody:
        return error_response(
            422,
            "invalid_request",
            "The request body was not valid JSON.",
            request_id=request_id,
        )
    except ValidationError as exc:
        return validation_error_response(exc, request_id=request_id)
    except AppError as exc:
        return app_error_response(exc, request_id=request_id)
    except Exception:
        logger.exception("Unhandled Lambda route error [%s]", request_id)
        return error_response(
            500,
            "internal_error",
            "Something went wrong on our side.",
            request_id=request_id,
        )
