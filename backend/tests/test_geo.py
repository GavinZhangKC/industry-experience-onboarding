import math

from app.lib.geo import (
    decode_polyline,
    distance_point_to_path_m,
    encode_polyline,
    haversine_m,
)


def test_haversine_known_distance():
    # Flinders Street Station to Southern Cross Station is roughly 1.3 km.
    d = haversine_m(-37.8183, 144.9671, -37.8184, 144.9525)
    assert 1200 < d < 1400


def test_polyline_roundtrip():
    points = [(-37.8183, 144.9671), (-37.8150, 144.9640), (-37.8102, 144.9628)]
    decoded = decode_polyline(encode_polyline(points))
    assert len(decoded) == len(points)
    for (alat, alng), (blat, blng) in zip(points, decoded):
        assert math.isclose(alat, blat, abs_tol=1e-5)
        assert math.isclose(alng, blng, abs_tol=1e-5)


def test_point_on_path_is_near_zero():
    path = [(-37.8183, 144.9671), (-37.8102, 144.9628)]
    assert distance_point_to_path_m(-37.8183, 144.9671, path) < 1


def test_point_beside_segment_not_only_vertices():
    """A point near the middle of a long segment must be detected, even though
    it is far from both endpoints."""
    path = [(-37.8200, 144.9600), (-37.8100, 144.9600)]
    d = distance_point_to_path_m(-37.8150, 144.9603, path)
    assert d < 40


def test_empty_path_is_infinite():
    assert distance_point_to_path_m(-37.81, 144.96, []) == float("inf")
