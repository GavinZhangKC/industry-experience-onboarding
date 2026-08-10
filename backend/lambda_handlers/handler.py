"""Shared Lambda Function URL entry point for the current HTTP API paths."""

from typing import Any

from lambda_handlers import quiet_spaces, routes
from lambda_handlers.common import error_response, get_path, get_request_id


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Dispatch one Function URL to the existing logical endpoint adapters."""
    path = get_path(event)
    if path == routes.ROUTES_PATH:
        return routes.handler(event, context)
    if path == quiet_spaces.QUIET_SPACES_PATH:
        return quiet_spaces.handler(event, context)

    return error_response(
        404,
        "not_found",
        "The requested endpoint was not found.",
        request_id=get_request_id(event, context),
    )
