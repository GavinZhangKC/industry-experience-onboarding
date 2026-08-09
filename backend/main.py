"""Vercel entry point for the existing FastAPI application.

AWS continues to use ``lambda_handlers.handler.handler``.  Vercel imports the
ASGI ``app`` below, so both deployment targets share the same service layer.
"""

from app.main import app

__all__ = ["app"]
