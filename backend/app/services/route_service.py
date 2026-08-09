"""BE-F1 orchestration: validate, fetch routes, score them, return JSON.

No FastAPI import anywhere in this file. It takes plain arguments and returns a
Pydantic model, which is what makes the eventual move to Lambda a wrapper job
rather than a rewrite.
"""

from datetime import datetime, timezone

from app.clients.maps_client import MapsClient
from app.config import Settings
from app.errors import NoRoutesFound, OutOfServiceArea
from app.lib.data_store import DataStore
from app.lib.geo import decode_polyline
from app.schemas import RouteOption, RouteRequest, RouteResponse
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
    store: DataStore,
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
                ),
            )
        )

    # Calmest route first, so "Route A" is always the least overwhelming option.
    # This is a product decision, not a technical one — sort by distance instead
    # if the team decides the fastest route should lead.
    scored.sort(key=lambda pair: pair[0])
    routes = []
    for position, (_, option) in enumerate(scored):
        routes.append(option.model_copy(update={"label": f"Route {ROUTE_LABELS[position]}"}))

    return RouteResponse(
        routes=routes,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
