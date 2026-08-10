"""AWS Lambda Function URL adapter for the health endpoint."""

import logging
from typing import Any

from app.config import get_settings
from app.lib.data_store import get_configured_data_store
from lambda_handlers.common import error_response, get_method, get_path, get_request_id, json_response

logger = logging.getLogger(__name__)

HEALTH_PATH = "/health"


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle GET /health with the same payload as the FastAPI endpoint."""
    request_id = get_request_id(event, context)
    if get_path(event) != HEALTH_PATH:
        return error_response(404, "not_found", "The requested endpoint was not found.", request_id=request_id)
    if get_method(event) != "GET":
        return error_response(405, "method_not_allowed", "This endpoint only accepts GET requests.", request_id=request_id, headers={"Allow": "GET"})

    try:
        settings = get_settings()
        store = get_configured_data_store(settings)
        return json_response(
            200,
            {
                "status": "ok",
                "maps_provider": settings.maps_provider,
                "busy_areas": len(store.busy_areas),
                "quiet_spaces": len(store.quiet_spaces),
            },
            request_id=request_id,
        )
    except Exception:
        logger.exception("Unhandled Lambda health error [%s]", request_id)
        return error_response(500, "internal_error", "Something went wrong on our side.", request_id=request_id)
