"""AWS Lambda Function URL adapter for BE-F3 quiet spaces."""

import logging
from typing import Any

from pydantic import ValidationError

from app.config import get_settings
from app.errors import AppError
from app.lib.data_store import get_configured_data_store
from app.schemas import QuietSpaceQuery
from app.services.refuge_service import find_quiet_spaces
from lambda_handlers.common import (
    app_error_response,
    error_response,
    get_method,
    get_path,
    get_request_id,
    json_response,
    validation_error_response,
)

logger = logging.getLogger(__name__)

QUIET_SPACES_PATH = "/api/v1/quiet-spaces"


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /api/v1/quiet-spaces from a Function URL event."""
    request_id = get_request_id(event, context)
    path = get_path(event)
    method = get_method(event)

    if path != QUIET_SPACES_PATH:
        return error_response(
            404,
            "not_found",
            "The requested endpoint was not found.",
            request_id=request_id,
        )
    if method != "GET":
        return error_response(
            405,
            "method_not_allowed",
            "This endpoint only accepts GET requests.",
            request_id=request_id,
            headers={"Allow": "GET"},
        )

    try:
        query = QuietSpaceQuery.model_validate(
            event.get("queryStringParameters") or {}
        )
        settings = get_settings()
        radius_m = (
            query.radius_m
            if query.radius_m is not None
            else settings.default_radius_metres
        )
        result = find_quiet_spaces(
            query.lat,
            query.lng,
            radius_m=radius_m,
            limit=query.limit,
            category=query.category,
            store=get_configured_data_store(settings),
            settings=settings,
        )
        return json_response(
            200,
            result.model_dump(mode="json"),
            request_id=request_id,
        )
    except ValidationError as exc:
        return validation_error_response(exc, request_id=request_id)
    except AppError as exc:
        return app_error_response(exc, request_id=request_id)
    except Exception:
        logger.exception("Unhandled Lambda quiet-space error [%s]", request_id)
        return error_response(
            500,
            "internal_error",
            "Something went wrong on our side.",
            request_id=request_id,
        )
