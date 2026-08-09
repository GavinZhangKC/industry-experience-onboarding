from types import SimpleNamespace

import pytest

from app.config import Settings
from app.errors import OutOfServiceArea
from app.services.refuge_service import find_quiet_spaces


SPACES = [
    {
        "id": "farther",
        "name": "Farther Park",
        "type": "park",
        "lat": -37.8140,
        "lng": 144.9740,
    },
    {
        "id": "nearest",
        "name": "Nearest Library",
        "type": "library",
        "lat": -37.8140,
        "lng": 144.9705,
    },
    {
        "id": "outside",
        "name": "Distant Garden",
        "type": "garden",
        "lat": -37.8500,
        "lng": 145.0000,
    },
]


def _settings() -> Settings:
    return Settings(_env_file=None)


def test_find_quiet_spaces_filters_sorts_and_limits_results():
    result = find_quiet_spaces(
        -37.8140,
        144.9700,
        radius_m=1000,
        limit=1,
        store=SimpleNamespace(quiet_spaces=SPACES),
        settings=_settings(),
    )

    assert [space.id for space in result.quiet_spaces] == ["nearest"]
    assert result.quiet_spaces[0].distance_m > 0
    assert result.radius_m == 1000
    assert result.message is None


def test_find_quiet_spaces_returns_normal_empty_result():
    result = find_quiet_spaces(
        -37.8000,
        144.9300,
        radius_m=100,
        limit=5,
        store=SimpleNamespace(quiet_spaces=SPACES),
        settings=_settings(),
    )

    assert result.quiet_spaces == []
    assert "No quiet spaces found within 100 metres" in result.message


def test_find_quiet_spaces_rejects_location_outside_service_area():
    with pytest.raises(OutOfServiceArea):
        find_quiet_spaces(
            -38.5,
            144.97,
            radius_m=500,
            limit=5,
            store=SimpleNamespace(quiet_spaces=SPACES),
            settings=_settings(),
        )
