"""US 2.2 — predictive alerts service.

Kept as a thin, separate service (rather than folding into scoring_service)
because it answers a different question: not "how calm is this specific
route right now" but "which areas, city-wide, are trending busier". Same
separation-of-concerns reasoning as refuge_service being independent of
route_service.
"""

from datetime import datetime, timezone

from app.lib.data_store import ReferenceDataStore
from app.schemas import PredictiveAlert, PredictiveAlertsResponse

# Below this, a rising trend is treated as noise (sensor jitter, one extra
# pedestrian at a quiet sensor swinging the percentage wildly) rather than a
# real signal worth alerting on.
MIN_PERCENT_INCREASE_TO_ALERT = 20.0


def _message_for(alert_area: dict) -> str:
    pct = alert_area["percent_increase"]
    name = alert_area["name"]
    if pct >= 75:
        return f"{name} is trending sharply busier — expect high pedestrian activity within the hour."
    return f"{name} is trending busier than usual — worth checking before you head that way."


def get_predictive_alerts(*, store: ReferenceDataStore) -> PredictiveAlertsResponse:
    raw = store.trending_areas
    alerts = [
        PredictiveAlert(
            id=area["id"],
            name=area["name"],
            lat=area["lat"],
            lng=area["lng"],
            percent_increase=area["percent_increase"],
            message=_message_for(area),
        )
        for area in raw
        if area["percent_increase"] >= MIN_PERCENT_INCREASE_TO_ALERT
    ]
    # Worst-trending first — the one thing a user glancing at this list needs
    # to see without scrolling.
    alerts.sort(key=lambda a: a.percent_increase, reverse=True)
    return PredictiveAlertsResponse(
        alerts=alerts,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
