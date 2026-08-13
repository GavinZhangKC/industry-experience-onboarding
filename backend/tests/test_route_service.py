import asyncio
from types import SimpleNamespace

import pytest

from app.clients.maps_client import RawRoute, RawRouteStep
from app.config import Settings
from app.errors import NoRoutesFound, OutOfServiceArea
from app.lib.geo import encode_polyline
from app.schemas import Coordinate, RouteRequest
from app.services.route_service import plan_routes


ORIGIN = Coordinate(lat=-37.8113, lng=144.9541)
DESTINATION = Coordinate(lat=-37.8140, lng=144.9737)


class FakeMapsClient:
    def __init__(self, routes: list[RawRoute]):
        self.routes = routes
        self.calls: list[tuple[tuple[float, float], tuple[float, float], int]] = []

    async def walking_routes(self, origin, destination, alternatives):
        self.calls.append((origin, destination, alternatives))
        return self.routes


def _raw_routes() -> list[RawRoute]:
    direct = encode_polyline(
        [(ORIGIN.lat, ORIGIN.lng), (DESTINATION.lat, DESTINATION.lng)]
    )
    alternative = encode_polyline(
        [
            (ORIGIN.lat, ORIGIN.lng),
            (-37.8070, 144.9630),
            (DESTINATION.lat, DESTINATION.lng),
        ]
    )
    return [
        RawRoute(distance_m=1800, duration_s=1300, polyline=direct, steps=[]),
        RawRoute(distance_m=2200, duration_s=1600, polyline=alternative, steps=[]),
    ]


def _settings() -> Settings:
    # Ignore a developer's local .env so these tests are deterministic.
    return Settings(_env_file=None)


def _request(origin: Coordinate = ORIGIN, destination: Coordinate = DESTINATION):
    return RouteRequest(origin=origin, destination=destination, alternatives=2)


def test_plan_routes_carries_navigation_steps_through_to_response():
    maps_client = FakeMapsClient(
        [
            RawRoute(
                distance_m=500,
                duration_s=360,
                polyline=encode_polyline([(ORIGIN.lat, ORIGIN.lng), (DESTINATION.lat, DESTINATION.lng)]),
                steps=[
                    RawRouteStep(instruction="Head north on Example St", distance_m=200, duration_s=150, polyline="abc"),
                    RawRouteStep(instruction="Arrive at your destination", distance_m=300, duration_s=210, polyline="def"),
                ],
            )
        ]
    )
    store = SimpleNamespace(busy_areas=[])

    response = asyncio.run(
        plan_routes(_request(), maps_client=maps_client, store=store, settings=_settings())
    )

    assert len(response.routes) == 1
    assert len(response.routes[0].steps) == 2
    assert response.routes[0].steps[0].instruction == "Head north on Example St"
    assert response.routes[0].steps[-1].instruction == "Arrive at your destination"


def test_plan_routes_returns_requested_route_fields():
    maps_client = FakeMapsClient(_raw_routes())
    store = SimpleNamespace(busy_areas=[])

    response = asyncio.run(
        plan_routes(
            _request(),
            maps_client=maps_client,
            store=store,
            settings=_settings(),
        )
    )

    assert maps_client.calls == [
        ((ORIGIN.lat, ORIGIN.lng), (DESTINATION.lat, DESTINATION.lng), 2)
    ]
    assert len(response.routes) == 2
    assert [route.label for route in response.routes] == ["Route A", "Route B"]
    for route in response.routes:
        assert route.distance_m > 0
        assert route.duration_s > 0
        assert route.polyline


def test_plan_routes_no_threshold_leaves_exceeds_threshold_none():
    """Unset threshold must mean 'not applicable', not False — existing
    callers that never send sensitivity_threshold shouldn't see routes
    marked as newly 'within limits' by default."""
    maps_client = FakeMapsClient(_raw_routes())
    store = SimpleNamespace(busy_areas=[])

    response = asyncio.run(
        plan_routes(
            _request(),
            maps_client=maps_client,
            store=store,
            settings=_settings(),
        )
    )

    assert all(route.exceeds_threshold is None for route in response.routes)
    assert response.all_routes_exceed_threshold is False


def test_plan_routes_flags_routes_above_threshold():
    """US 1.3: a busy area sitting on the route path should push its score
    above a strict threshold, and get flagged."""
    maps_client = FakeMapsClient(_raw_routes())
    # Placed directly on the direct route's straight-line path, close enough
    # to guarantee proximity_metres catches it with the default config.
    store = SimpleNamespace(
        busy_areas=[
            {"id": "b1", "name": "Busy corner", "type": "pedestrian_sensor", "lat": -37.81265, "lng": 144.9639, "weight": 5}
        ]
    )
    request = RouteRequest(
        origin=ORIGIN, destination=DESTINATION, alternatives=2, sensitivity_threshold=10
    )

    response = asyncio.run(
        plan_routes(request, maps_client=maps_client, store=store, settings=_settings())
    )

    assert any(route.exceeds_threshold is True for route in response.routes)


def test_plan_routes_all_exceed_threshold_flag_true_when_every_route_flagged():
    maps_client = FakeMapsClient(_raw_routes())
    store = SimpleNamespace(
        busy_areas=[
            {"id": "b1", "name": "Busy corner", "type": "pedestrian_sensor", "lat": -37.81265, "lng": 144.9639, "weight": 5},
            {"id": "b2", "name": "Also busy", "type": "pedestrian_sensor", "lat": -37.807, "lng": 144.963, "weight": 5},
        ]
    )
    request = RouteRequest(
        origin=ORIGIN, destination=DESTINATION, alternatives=2, sensitivity_threshold=0
    )

    response = asyncio.run(
        plan_routes(request, maps_client=maps_client, store=store, settings=_settings())
    )

    assert response.all_routes_exceed_threshold is True
    assert all(route.exceeds_threshold for route in response.routes)



    maps_client = FakeMapsClient([])

    with pytest.raises(NoRoutesFound):
        asyncio.run(
            plan_routes(
                _request(),
                maps_client=maps_client,
                store=SimpleNamespace(busy_areas=[]),
                settings=_settings(),
            )
        )


def test_plan_routes_rejects_a_point_outside_the_service_area_before_provider_call():
    maps_client = FakeMapsClient(_raw_routes())
    outside_melbourne = Coordinate(lat=-38.5, lng=144.96)

    with pytest.raises(OutOfServiceArea):
        asyncio.run(
            plan_routes(
                _request(origin=outside_melbourne),
                maps_client=maps_client,
                store=SimpleNamespace(busy_areas=[]),
                settings=_settings(),
            )
        )

    assert maps_client.calls == []
