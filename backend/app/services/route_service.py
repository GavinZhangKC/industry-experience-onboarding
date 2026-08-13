"""BE-F1 orchestration: validate, fetch routes, score them, return JSON.

No FastAPI import anywhere in this file. It takes plain arguments and returns a
Pydantic model, which is what makes the eventual move to Lambda a wrapper job
rather than a rewrite.
"""

from datetime import datetime, timezone

from app.clients.maps_client import MapsClient
from app.config import Settings
from app.errors import NoRoutesFound, OutOfServiceArea
from app.lib.data_store import ReferenceDataStore
from app.lib.geo import decode_polyline
from app.schemas import RouteOption, RouteRequest, RouteResponse, RouteStep
from app.services.scoring_service import score_route

ROUTE_LABELS = "ABCDE"


def guard_service_area(lat: float, lng: float, settings: Settings) -> None:
    within = (
        settings.min_lat <= lat <= settings.max_lat
        and settings.min_lng <= lng <= settings.max_lng
    )
    if not within:
        raise OutOfServiceArea()


async def plan_routes(
    request: RouteRequest,
    *,
    maps_client: MapsClient,
    store: ReferenceDataStore,
    settings: Settings,
) -> RouteResponse:
    guard_service_area(request.origin.lat, request.origin.lng, settings)
    guard_service_area(request.destination.lat, request.destination.lng, settings)

    raw_routes = await maps_client.walking_routes(
        (request.origin.lat, request.origin.lng),
        (request.destination.lat, request.destination.lng),
        request.alternatives,
    )
    if not raw_routes:
        raise NoRoutesFound()

    busy_areas = store.busy_areas
    scored: list[tuple[int, RouteOption]] = []

    for index, raw in enumerate(raw_routes):
        path = decode_polyline(raw.polyline)
        sensory = score_route(
            path,
            busy_areas,
            proximity_m=settings.proximity_metres,
            low_threshold=settings.low_threshold,
            medium_threshold=settings.medium_threshold,
        )
        scored.append(
            (
                sensory.score,
                RouteOption(
                    id=f"route-{index}",
                    label="",  # assigned after sorting
                    distance_m=raw.distance_m,
                    duration_s=raw.duration_s,
                    polyline=raw.polyline,
                    sensory=sensory,
                    steps=[
                        RouteStep(
                            instruction=step.instruction,
                            distance_m=step.distance_m,
                            duration_s=step.duration_s,
                            polyline=step.polyline,
                        )
                        for step in raw.steps
                    ],
                ),
            )
        )

    # Calmest route first, so "Route A" is always the least overwhelming option.
    # This is a product decision, not a technical one — sort by distance instead
    # if the team decides the fastest route should lead.
    scored.sort(key=lambda pair: pair[0])
    routes = []
    for position, (score, option) in enumerate(scored):
        exceeds = (
            score > request.sensitivity_threshold
            if request.sensitivity_threshold is not None
            else None
        )
        routes.append(
            option.model_copy(
                update={"label": f"Route {ROUTE_LABELS[position]}", "exceeds_threshold": exceeds}
            )
        )

    # Only meaningful when a threshold was actually requested — with no
    # threshold, exceeds_threshold is None on every route, and this should
    # read as "not applicable", not "true".
    all_exceed = (
        request.sensitivity_threshold is not None
        and all(r.exceeds_threshold for r in routes)
    )

    return RouteResponse(
        routes=routes,
        generated_at=datetime.now(timezone.utc).isoformat(),
        all_routes_exceed_threshold=all_exceed,
    )
