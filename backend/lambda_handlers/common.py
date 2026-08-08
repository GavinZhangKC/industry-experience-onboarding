"""Shared helpers for Lambda Function URL handlers.

The service layer deliberately has no AWS dependencies. These helpers translate
between Lambda's HTTP payload format and the API's existing JSON response shape.
"""

import base64
import binascii
import json
import uuid
from typing import Any

from pydantic import ValidationError

from app.errors import AppError

JSON_HEADERS = {"Content-Type": "application/json"}


class MalformedBody(ValueError):
    """The Function URL request body could not be decoded as JSON."""


def get_request_id(event: dict[str, Any], context: Any) -> str:
    headers = event.get("headers") or {}
    supplied_id = next(
        (
            value
            for name, value in headers.items()
            if name.lower() == "x-request-id" and value
        ),
        None,
    )
    function_url_id = (event.get("requestContext") or {}).get("requestId")
    lambda_id = getattr(context, "aws_request_id", None)
    return supplied_id or function_url_id or lambda_id or uuid.uuid4().hex[:12]


def get_method(event: dict[str, Any]) -> str:
    request_context = event.get("requestContext") or {}
    http = request_context.get("http") or {}
    return str(http.get("method") or "").upper()


def get_path(event: dict[str, Any]) -> str:
    request_context = event.get("requestContext") or {}
    http = request_context.get("http") or {}
    return str(event.get("rawPath") or http.get("path") or "")


def json_response(
    status_code: int,
    body: dict[str, Any],
    *,
    request_id: str,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    response_headers = {**JSON_HEADERS, "X-Request-ID": request_id}
    if headers:
        response_headers.update(headers)
    return {
        "statusCode": status_code,
        "headers": response_headers,
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }


def error_response(
    status_code: int,
    code: str,
    message: str,
    *,
    request_id: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details:
        body["error"]["details"] = details
    return json_response(
        status_code, body, request_id=request_id, headers=headers
    )


def app_error_response(exc: AppError, *, request_id: str) -> dict[str, Any]:
    return error_response(
        exc.status_code,
        exc.code,
        exc.message,
        request_id=request_id,
        details=exc.details,
    )


def validation_error_response(
    exc: ValidationError, *, request_id: str
) -> dict[str, Any]:
    fields = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "problem": error["msg"],
        }
        for error in exc.errors()
    ]
    return error_response(
        422,
        "invalid_request",
        "The request data was not valid.",
        request_id=request_id,
        details={"fields": fields},
    )


def parse_json_body(event: dict[str, Any]) -> Any:
    body = event.get("body")
    if not isinstance(body, str) or not body.strip():
        raise MalformedBody("Request body must contain JSON.")

    if event.get("isBase64Encoded", False):
        try:
            body = base64.b64decode(body, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise MalformedBody("Request body was not valid base64 JSON.") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise MalformedBody("Request body was not valid JSON.") from exc
