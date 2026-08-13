import asyncio

from app.clients.maps_client import GoogleMapsClient, MockMapsClient


def test_mock_client_produces_steps_covering_the_whole_route():
    client = MockMapsClient()
    routes = asyncio.run(
        client.walking_routes((-37.8113, 144.9541), (-37.8140, 144.9737), alternatives=1)
    )
    route = routes[0]

    assert len(route.steps) > 0
    # Every step's distance should be a real, positive slice of the route —
    # not zero, not the full route length repeated.
    assert all(step.distance_m > 0 for step in route.steps)
    total_step_distance = sum(step.distance_m for step in route.steps)
    # Chunked haversine sums won't exactly equal the route total (rounding,
    # and each chunk includes its own endpoints), but should be in the same
    # ballpark rather than wildly off.
    assert abs(total_step_distance - route.distance_m) < route.distance_m * 0.5

    assert route.steps[-1].instruction == "Arrive at your destination"


def test_mock_client_steps_have_encoded_polylines():
    client = MockMapsClient()
    routes = asyncio.run(
        client.walking_routes((-37.8113, 144.9541), (-37.8140, 144.9737), alternatives=1)
    )
    assert all(step.polyline for step in routes[0].steps)


def test_google_client_parses_steps_from_legs():
    route = {
        "distanceMeters": 500,
        "duration": "360s",
        "polyline": {"encodedPolyline": "route_poly"},
        "legs": [
            {
                "steps": [
                    {
                        "navigationInstruction": {"instructions": "Turn left onto Flinders St"},
                        "distanceMeters": 100,
                        "staticDuration": "80s",
                        "polyline": {"encodedPolyline": "step1"},
                    },
                    {
                        # Deliberately missing navigationInstruction — Google
                        # doesn't always provide one for very short steps.
                        "distanceMeters": 50,
                        "staticDuration": "40s",
                        "polyline": {"encodedPolyline": "step2"},
                    },
                ]
            }
        ],
    }

    steps = GoogleMapsClient._parse_steps(route)

    assert len(steps) == 2
    assert steps[0].instruction == "Turn left onto Flinders St"
    assert steps[0].distance_m == 100
    assert steps[0].duration_s == 80
    # Missing instruction falls back to something non-empty, not a blank string.
    assert steps[1].instruction == "Continue"


def test_google_client_parses_steps_across_multiple_legs():
    """A route with a via-point (or any multi-leg route) should concatenate
    steps from every leg in order, not just the first."""
    route = {
        "legs": [
            {"steps": [{"navigationInstruction": {"instructions": "Leg 1 step"}, "distanceMeters": 10, "staticDuration": "8s", "polyline": {"encodedPolyline": "a"}}]},
            {"steps": [{"navigationInstruction": {"instructions": "Leg 2 step"}, "distanceMeters": 20, "staticDuration": "16s", "polyline": {"encodedPolyline": "b"}}]},
        ]
    }

    steps = GoogleMapsClient._parse_steps(route)

    assert [s.instruction for s in steps] == ["Leg 1 step", "Leg 2 step"]
