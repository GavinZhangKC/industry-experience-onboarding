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
from app.lib.geo import encode_polyline, haversine_m

logger = logging.getLogger(__name__)

GOOGLE_ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
WALKING_SPEED_MPS = 1.35


@dataclass
class RawRouteStep:
    instruction: str
    distance_m: int
    duration_s: int
    polyline: str


@dataclass
class RawRoute:
    distance_m: int
    duration_s: int
    polyline: str
    steps: list[RawRouteStep]


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
                    steps=self._synthetic_steps(path),
                )
            )
        return routes

    @staticmethod
    def _synthetic_steps(path: list[tuple[float, float]], chunk_count: int = 4) -> list[RawRouteStep]:
        """Splits the already-interpolated path into evenly-sized chunks with
        generic, honestly-synthetic instructions — mock mode has no real
        street network, so it cannot know actual street names or genuine turn
        directions. This exists purely so the navigation UI has something to
        render and can be exercised end-to-end without a Google key."""
        if len(path) < 2:
            return []
        chunk_size = max(1, len(path) // chunk_count)
        labels = [
            "Head toward your destination",
            "Continue along the path",
            "Continue toward your destination",
            "Approach your destination",
        ]
        steps: list[RawRouteStep] = []
        for i in range(0, len(path) - 1, chunk_size):
            chunk = path[i : min(i + chunk_size + 1, len(path))]
            if len(chunk) < 2:
                continue
            distance = sum(
                haversine_m(a[0], a[1], b[0], b[1]) for a, b in zip(chunk, chunk[1:])
            )
            label_index = min(len(steps), len(labels) - 1)
            steps.append(
                RawRouteStep(
                    instruction=labels[label_index],
                    distance_m=int(round(distance)),
                    duration_s=int(round(distance / WALKING_SPEED_MPS)),
                    polyline=encode_polyline(chunk),
                )
            )
        if steps:
            steps[-1] = RawRouteStep(
                instruction="Arrive at your destination",
                distance_m=steps[-1].distance_m,
                duration_s=steps[-1].duration_s,
                polyline=steps[-1].polyline,
            )
        return steps

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
            "X-Goog-FieldMask": (
                "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline,"
                "routes.legs.steps.navigationInstruction.instructions,"
                "routes.legs.steps.distanceMeters,routes.legs.steps.staticDuration,"
                "routes.legs.steps.polyline.encodedPolyline"
            ),
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

        raw = response.json().get("routes", [])
        if not raw:
            raise NoRoutesFound()

        routes = []
        for route in raw[:alternatives]:
            duration = route.get("duration", "0s")
            routes.append(
                RawRoute(
                    distance_m=int(route.get("distanceMeters", 0)),
                    duration_s=int(float(str(duration).rstrip("s") or 0)),
                    polyline=route.get("polyline", {}).get("encodedPolyline", ""),
                    steps=self._parse_steps(route),
                )
            )
        return routes

    @staticmethod
    def _parse_steps(route: dict) -> list[RawRouteStep]:
        steps: list[RawRouteStep] = []
        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                step_duration = step.get("staticDuration", "0s")
                instruction = (
                    step.get("navigationInstruction", {}).get("instructions")
                    # Not every step (e.g. a short initial/final segment) has a
                    # turn instruction from Google — fall back rather than
                    # showing a blank line in the UI.
                    or "Continue"
                )
                steps.append(
                    RawRouteStep(
                        instruction=instruction,
                        distance_m=int(step.get("distanceMeters", 0)),
                        duration_s=int(float(str(step_duration).rstrip("s") or 0)),
                        polyline=step.get("polyline", {}).get("encodedPolyline", ""),
                    )
                )
        return steps


def get_maps_client(settings: Settings) -> MapsClient:
    if settings.maps_provider == "google":
        return GoogleMapsClient(settings)
    logger.info("Using mock mapping provider (set MAPS_PROVIDER=google to switch)")
    return MockMapsClient()
