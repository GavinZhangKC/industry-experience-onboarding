"""FastAPI application factory.

This is the ONLY file that knows the app is served by FastAPI/uvicorn. The
services underneath take plain arguments and return Pydantic models, so moving
to Lambda later means adding thin handler wrappers, not rewriting logic.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import health, predictive_alerts, quiet_spaces, refuge_detour, routes
from app.config import get_settings
from app.errors import AppError
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware

logger = logging.getLogger(__name__)


def _envelope(request: Request, status: int, code: str, message: str, details=None):
    """BE-F5: one error shape for every failure, everywhere."""
    body = {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", None),
        }
    }
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = FastAPI(
        title="Sensory-Aware Route Planner API",
        version="0.1.0",
        description="Walking routes with a sensory rating, and nearby quiet spaces.",
    )

    # Middleware runs bottom-up: request context is outermost so every response,
    # including a 429 from the rate limiter, carries a request id.
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    app.add_middleware(RequestContextMiddleware)

    # BE-F5: an explicit allow-list. Never "*" once credentials are involved.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    app.include_router(health.router)
    app.include_router(routes.router)
    app.include_router(quiet_spaces.router)
    app.include_router(refuge_detour.router)
    app.include_router(predictive_alerts.router)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return _envelope(request, exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        fields = [
            {"field": ".".join(str(p) for p in err["loc"][1:]), "problem": err["msg"]}
            for err in exc.errors()
        ]
        return _envelope(
            request,
            422,
            "invalid_request",
            "The request data was not valid.",
            {"fields": fields},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        # Log the real cause; return nothing about it. Stack traces and library
        # internals in an HTTP response are an information disclosure risk.
        logger.exception(
            "Unhandled error [%s]", getattr(request.state, "request_id", None)
        )
        return _envelope(
            request, 500, "internal_error", "Something went wrong on our side."
        )

    return app


app = create_app()
