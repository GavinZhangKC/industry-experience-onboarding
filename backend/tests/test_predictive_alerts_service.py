from types import SimpleNamespace

from app.services.predictive_alerts_service import get_predictive_alerts


def test_no_trending_areas_returns_empty_list():
    store = SimpleNamespace(trending_areas=[])
    response = get_predictive_alerts(store=store)
    assert response.alerts == []


def test_small_increase_is_filtered_as_noise():
    """A 5% rise (e.g. 20 -> 21 pedestrians) shouldn't alert anyone."""
    store = SimpleNamespace(
        trending_areas=[
            {"id": "s1", "name": "Quiet Lane", "lat": -37.81, "lng": 144.96, "latest": 21, "prev": 20, "percent_increase": 5.0}
        ]
    )
    response = get_predictive_alerts(store=store)
    assert response.alerts == []


def test_genuine_rise_produces_an_alert_sorted_worst_first():
    store = SimpleNamespace(
        trending_areas=[
            {"id": "s1", "name": "Moderate Rise St", "lat": -37.81, "lng": 144.96, "latest": 60, "prev": 40, "percent_increase": 50.0},
            {"id": "s2", "name": "Sharp Rise Mall", "lat": -37.82, "lng": 144.97, "latest": 90, "prev": 30, "percent_increase": 200.0},
        ]
    )
    response = get_predictive_alerts(store=store)

    assert [a.id for a in response.alerts] == ["s2", "s1"]
    assert "sharply" in response.alerts[0].message.lower()
    assert "sharply" not in response.alerts[1].message.lower()
