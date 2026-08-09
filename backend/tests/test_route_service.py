import asyncio
from types import SimpleNamespace

import pytest

from app.clients.maps_client import RawRoute
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
        RawRoute(distance_m=1800, duration_s=1300, polyline=direct),
        RawRoute(distance_m=2200, duration_s=1600, polyline=alternative),
    ]


def _settings() -> Settings:
    # Ignore a developer's local .env so these tests are deterministic.
    return Settings(_env_file=None)


def _request(origin: Coordinate = ORIGIN, destination: Coordinate = DESTINATION):
    return RouteRequest(origin=origin, destination=destination, alternatives=2)


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


def test_plan_routes_raises_when_provider_returns_no_routes():
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
