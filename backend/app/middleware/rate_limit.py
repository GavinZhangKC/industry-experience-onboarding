"""BE-F5: basic rate limiting.

A fixed window counter per client IP, held in process memory.

Known limit, and worth saying out loud rather than discovering later: this
counter is per process. Behind more than one worker, or on Lambda where each
concurrent execution has its own memory, each instance keeps a separate count,
so the effective limit multiplies. It is adequate for the MVP and for a demo.
Anything beyond that needs the counter in a shared store (Redis) or the limit
enforced at the edge (API Gateway usage plans, or WAF rate-based rules).
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

# /refuge-detour makes two upstream mapping calls per request (current->refuge,
# refuge->destination) instead of one, so it costs the mapping provider twice
# as much as every other endpoint. Uncontrolled traffic here is double the
# financial exposure for the same request volume — a flagged risk-matrix item
# — so it counts double against the *same* shared limit rather than getting
# its own separate counter, which would let it double the real request volume
# before either limit trips. Simpler than a second counter, same effect.
PATH_WEIGHTS = {"/api/v1/refuge-detour": 2}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, max_requests: int, window_seconds: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        # X-Forwarded-For is only trustworthy behind a proxy you control.
        # Once deployed behind API Gateway or a load balancer, read the left-most
        # entry; until then, the socket address is the honest answer.
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        key = self._client_key(request)
        weight = PATH_WEIGHTS.get(request.url.path, 1)
        now = time.monotonic()
        cutoff = now - self.window_seconds

        hits = [(t, w) for t, w in self._hits[key] if t > cutoff]
        used = sum(w for _, w in hits)

        if used + weight > self.max_requests:
            self._hits[key] = hits
            retry_after = int(self.window_seconds - (now - hits[0][0])) + 1 if hits else self.window_seconds
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please slow down and try again shortly.",
                        "request_id": getattr(request.state, "request_id", None),
                    }
                },
            )

        hits.append((now, weight))
        self._hits[key] = hits

        # Opportunistic cleanup so the dict cannot grow without bound.
        if len(self._hits) > 2048:
            self._hits = defaultdict(
                list, {k: v for k, v in self._hits.items() if v and v[-1][0] > cutoff}
            )

        return await call_next(request)
