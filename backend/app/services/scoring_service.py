"""BE-F2: basic sensory scoring.

Design note, and it is the one that matters:

US1.1 acceptance criterion 4 says the Low/Medium/High label and the
plain-language explanation must come from the same underlying data so they can
never contradict each other. That is enforced structurally here — `_findings()`
runs once and produces a single list of factors; the score, the level and the
explanation are all derived from that same list. There is no second code path
that could drift.
"""

import math

from app.lib.geo import distance_point_to_path_m
from app.schemas import SensoryFactor, SensoryLevel, SensoryResult

# Controls how quickly the score climbs toward 100.
#
# A plain weighted sum saturates almost immediately in the CBD — four busy
# areas near a route is normal, not exceptional, so every route came back at
# 100/100 and "medium" never appeared. The exponential below keeps the score
# responsive across the whole range: one major hub lands around 39, two around
# 63, four around 87.
SATURATION_K = 9.0


def _findings(path, busy_areas, proximity_m: float) -> list[SensoryFactor]:
    factors: list[SensoryFactor] = []
    for area in busy_areas:
        distance = distance_point_to_path_m(area["lat"], area["lng"], path)
        if distance <= proximity_m:
            factors.append(
                SensoryFactor(
                    name=area["name"],
                    type=area["type"],
                    distance_m=int(round(distance)),
                    weight=int(area["weight"]),
                )
            )
    factors.sort(key=lambda f: (-f.weight, f.distance_m))
    return factors


def _score(factors: list[SensoryFactor], proximity_m: float) -> int:
    """Weight each factor by how close it sits to the path, then map the total
    onto 0-100 through a saturating curve."""
    raw = 0.0
    for factor in factors:
        closeness = 1.0 - (factor.distance_m / proximity_m)
        raw += factor.weight * max(0.0, closeness)
    return int(min(100, round(100 * (1 - math.exp(-raw / SATURATION_K)))))


def _level(score: int, low_threshold: int, medium_threshold: int) -> SensoryLevel:
    if score <= low_threshold:
        return "low"
    if score <= medium_threshold:
        return "medium"
    return "high"


def _explanation(level: SensoryLevel, factors: list[SensoryFactor]) -> str:
    if not factors:
        return "This route stays clear of the busy areas we track."

    names = [f.name for f in factors]
    lead = {
        "low": "Mostly quiet.",
        "medium": "Moderately busy.",
        "high": "Expect a busy route.",
    }[level]

    if len(names) == 1:
        detail = f"It passes close to {names[0]}."
    elif len(names) == 2:
        detail = f"It passes close to {names[0]} and {names[1]}."
    else:
        detail = (
            f"It passes close to {len(names)} busy areas, "
            f"including {names[0]} and {names[1]}."
        )
    return f"{lead} {detail}"


def score_route(
    path,
    busy_areas,
    *,
    proximity_m: float,
    low_threshold: int,
    medium_threshold: int,
) -> SensoryResult:
    factors = _findings(path, busy_areas, proximity_m)
    score = _score(factors, proximity_m)
    level = _level(score, low_threshold, medium_threshold)
    return SensoryResult(
        score=score,
        level=level,
        explanation=_explanation(level, factors),
        factors=factors,
    )
