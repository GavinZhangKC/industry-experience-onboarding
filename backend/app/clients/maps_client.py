"""BE-F1: the only place that talks to an external mapping provider.

BE-F5: the API key is read from settings (environment) and used server-side
only. It is never included in any response, so it cannot reach frontend code.
"""

import logging
import math
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.config import Settings
from app.errors import NoRoutesFound, UpstreamError
from app.lib.geo import decode_polyline, encode_polyline, haversine_m

logger = logging.getLogger(__name__)

GOOGLE_ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
WALKING_SPEED_MPS = 1.35


@dataclass
class RawRoute:
    distance_m: int
    duration_s: int
    polyline: str


class MapsClient(Protocol):
    async def walking_routes(
        self, origin: tuple[float, float], destination: tuple[float, float], alternatives: int
    ) -> list[RawRoute]: ...


class MockMapsClient:
    """Generates plausible alternative walking routes with no external call.

    This exists so the frontend and the scoring engine can be built and demoed
    before anyone has a billable Google key. Set MAPS_PROVIDER=google to swap.
    """

    async def walking_routes(self, origin, destination, alternatives) -> list[RawRoute]:
        (olat, olng), (dlat, dlng) = origin, destination
        routes: list[RawRoute] = []

        # Unit vector perpendicular to the direct line, so each alternative bows
        # out by a FIXED distance rather than one that scales with route length
        # (which collapses to a few metres on a short CBD walk).
        vlat, vlng = dlat - olat, dlng - olng
        norm = math.hypot(vlat, vlng) or 1e-9
        perp_lat, perp_lng = -vlng / norm, vlat / norm

        for i in range(alternatives):
            offset_deg = (i - (alternatives - 1) / 2) * 0.0030  # ~330 m per step
            mid = (
                (olat + dlat) / 2 + perp_lat * offset_deg,
                (olng + dlng) / 2 + perp_lng * offset_deg,
            )
            path = self._interpolate([(olat, olng), mid, (dlat, dlng)])
            distance = sum(
                haversine_m(a[0], a[1], b[0], b[1]) for a, b in zip(path, path[1:])
            )
            routes.append(
                RawRoute(
                    distance_m=int(round(distance)),
                    duration_s=int(round(distance / WALKING_SPEED_MPS)),
                    polyline=encode_polyline(path),
                )
            )
        return routes

    @staticmethod
    def _interpolate(anchors, per_leg: int = 14):
        path = [anchors[0]]
        for a, b in zip(anchors, anchors[1:]):
            for step in range(1, per_leg + 1):
                t = step / per_leg
                path.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        return path


class GoogleMapsClient:
    def __init__(self, settings: Settings):
        if not settings.google_maps_api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY is not set but MAPS_PROVIDER=google")
        self._key = settings.google_maps_api_key
        self._timeout = settings.request_timeout_seconds

    async def walking_routes(self, origin, destination, alternatives) -> list[RawRoute]:
        payload = {
            "origin": {"location": {"latLng": {"latitude": origin[0], "longitude": origin[1]}}},
            "destination": {
                "location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}
            },
            "travelMode": "WALK",
            "computeAlternativeRoutes": True,
        }
        headers = {
            "X-Goog-Api-Key": self._key,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(GOOGLE_ROUTES_URL, json=payload, headers=headers)
        except httpx.RequestError as exc:
            # Log the detail, return a generic message: never surface upstream
            # internals (or anything containing the key) to the client.
            logger.warning("Mapping provider unreachable: %s", exc)
            raise UpstreamError() from exc

        if response.status_code != 200:
            logger.warning("Mapping provider returned %s", response.status_code)
            raise UpstreamError()

        try:
            payload = response.json()
        except ValueError as exc:
            logger.warning("Mapping provider returned invalid JSON")
            raise UpstreamError() from exc

        raw = payload.get("routes", []) if isinstance(payload, dict) else []
        if not raw:
            raise NoRoutesFound()

        try:
            return [_parse_google_route(route) for route in raw[:alternatives]]
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("Mapping provider returned an invalid route: %s", exc)
            raise UpstreamError() from exc


def _parse_google_route(route: object) -> RawRoute:
    """Validate the small Google response surface the service relies on."""
    if not isinstance(route, dict):
        raise ValueError("route must be an object")

    distance = route.get("distanceMeters")
    if isinstance(distance, bool) or not isinstance(distance, int) or distance <= 0:
        raise ValueError("route distance must be a positive integer")

    duration = route.get("duration")
    if not isinstance(duration, str) or not duration.endswith("s"):
        raise ValueError("route duration must be seconds")
    duration_value = float(duration[:-1])
    duration_s = int(duration_value)
    if not math.isfinite(duration_value) or duration_s <= 0:
        raise ValueError("route duration must be positive")

    polyline = route.get("polyline", {}).get("encodedPolyline")
    if not isinstance(polyline, str):
        raise ValueError("route polyline must contain at least two points")
    points = decode_polyline(polyline)
    if len(points) < 2 or any(
        not (-90 <= lat <= 90 and -180 <= lng <= 180) for lat, lng in points
    ):
        raise ValueError("route polyline must contain valid coordinates")

    return RawRoute(
        distance_m=distance,
        duration_s=duration_s,
        polyline=polyline,
    )


def get_maps_client(settings: Settings) -> MapsClient:
    if settings.maps_provider == "google":
        return GoogleMapsClient(settings)
    logger.info("Using mock mapping provider (set MAPS_PROVIDER=google to switch)")
    return MockMapsClient()
