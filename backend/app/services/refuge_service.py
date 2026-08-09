"""BE-F3: nearest quiet spaces to a coordinate, and AC5's detour-and-rejoin."""

from datetime import datetime, timezone

from app.clients.maps_client import MapsClient
from app.config import Settings
from app.lib.data_store import ReferenceDataStore
from app.lib.geo import haversine_m
from app.schemas import (
    QuietSpace,
    QuietSpaceResponse,
    RefugeCategory,
    RefugeDetourRequest,
    RefugeDetourResponse,
    RefugeLeg,
    RouteRequest,
)
from app.services.route_service import guard_service_area, plan_routes

# AC4: green space vs indoor. One mapping, owned here, so the frontend never
# duplicates it — the backend returns `category` on every record instead.
_TYPE_TO_CATEGORY: dict[str, RefugeCategory] = {
    "park": "green_space",
    "garden": "green_space",
    "library": "indoor",
}


def _category_for(type_: str) -> RefugeCategory:
    return _TYPE_TO_CATEGORY.get(type_, "indoor")


def find_quiet_spaces(
    lat: float,
    lng: float,
    *,
    radius_m: int,
    limit: int,
    category: RefugeCategory | None = None,
    store: ReferenceDataStore,
    settings: Settings,
) -> QuietSpaceResponse:
    guard_service_area(lat, lng, settings)

    nearby: list[QuietSpace] = []
    for space in store.quiet_spaces:
        space_category = _category_for(space["type"])
        if category is not None and space_category != category:
            continue

        distance = haversine_m(lat, lng, space["lat"], space["lng"])
        if distance <= radius_m:
            nearby.append(
                QuietSpace(
                    id=space["id"],
                    name=space["name"],
                    type=space["type"],
                    category=space_category,
                    lat=space["lat"],
                    lng=space["lng"],
                    distance_m=int(round(distance)),
                    description=space.get(
                        "description", "A nearby place that may offer a quieter break."
                    ),
                )
            )

    # Category is filtered above, before this truncation — filtering after
    # `limit` is exactly the bug the `category` parameter exists to avoid.
    nearby.sort(key=lambda s: s.distance_m)
    nearby = nearby[:limit]

    # An empty result is a normal outcome, not an error — the prototype shows a
    # "expand the search area?" prompt, so the frontend needs a 200 with a
    # message rather than a 404 to render that.
    message = (
        None
        if nearby
        else f"No quiet spaces found within {radius_m} metres. Try expanding the search area."
    )

    return QuietSpaceResponse(quiet_spaces=nearby, radius_m=radius_m, message=message)


async def plan_refuge_detour(
    request: RefugeDetourRequest,
    *,
    maps_client: MapsClient,
    store: ReferenceDataStore,
    settings: Settings,
) -> RefugeDetourResponse:
    """AC5: show the detour to a refuge *and* the way back onto the original
    route. There's no waypoint-aware mapping call, so this chains two
    /routes-equivalent calls instead of one — current->refuge, then
    refuge->destination — and reuses plan_routes (so this shares its
    service-area guard and its scoring) rather than duplicating either.
    Between the two calls, all three input points (current, refuge,
    destination) get guarded: refuge is guarded as the destination of the
    first call and the origin of the second.

    A single waypoint-aware endpoint (one upstream call with an intermediate
    stop) would be cleaner than two full route calls, but the mock/Google
    routing client doesn't support one.
    """
    to_refuge = await plan_routes(
        RouteRequest(origin=request.current, destination=request.refuge, alternatives=2),
        maps_client=maps_client,
        store=store,
        settings=settings,
    )
    refuge_to_destination = await plan_routes(
        RouteRequest(origin=request.refuge, destination=request.destination, alternatives=2),
        maps_client=maps_client,
        store=store,
        settings=settings,
    )

    # plan_routes sorts calmest first, so index 0 is the calmest option for
    # each leg.
    leg1 = to_refuge.routes[0]
    leg2 = refuge_to_destination.routes[0]

    legs = [
        RefugeLeg(
            name="To refuge",
            distance_m=leg1.distance_m,
            duration_s=leg1.duration_s,
            polyline=leg1.polyline,
            sensory=leg1.sensory,
        ),
        RefugeLeg(
            name="Refuge to destination",
            distance_m=leg2.distance_m,
            duration_s=leg2.duration_s,
            polyline=leg2.polyline,
            sensory=leg2.sensory,
        ),
    ]

    return RefugeDetourResponse(
        legs=legs,
        total_distance_m=leg1.distance_m + leg2.distance_m,
        total_duration_s=leg1.duration_s + leg2.duration_s,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
