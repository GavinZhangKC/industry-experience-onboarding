"""Request and response models.

BE-F5: "validate incoming request data". Every inbound field is bounded here,
so a malformed or hostile payload is rejected before it reaches any service.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

SensoryLevel = Literal["low", "medium", "high"]

# AC4: filter refuges by green space vs indoor. Derived server-side from
# `type` (see refuge_service._category_for) so the frontend never duplicates
# the mapping.
RefugeCategory = Literal["green_space", "indoor"]


class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    alternatives: int = Field(3, ge=2, le=5)
    # US 1.3 — "alternative low-stimulation routes when crowd density exceeds
    # my preferred threshold". None means no preference filtering at all
    # (today's behaviour, unchanged for existing callers). Uses the same
    # 0-100 score scale as SensoryResult.score, so a caller can reasonably
    # pass settings.medium_threshold if they want "warn me above Medium".
    sensitivity_threshold: int | None = Field(None, ge=0, le=100)

    @model_validator(mode="after")
    def _origin_differs_from_destination(self):
        same = (
            abs(self.origin.lat - self.destination.lat) < 1e-6
            and abs(self.origin.lng - self.destination.lng) < 1e-6
        )
        if same:
            raise ValueError("origin and destination must be different points")
        return self


class SensoryFactor(BaseModel):
    """One busy area that this route passes near. These are the raw findings
    that BOTH the level and the explanation are derived from."""

    name: str
    type: str
    distance_m: int
    weight: int


class SensoryResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    level: SensoryLevel
    explanation: str
    factors: list[SensoryFactor]


class RouteStep(BaseModel):
    instruction: str
    distance_m: int
    duration_s: int
    polyline: str


class RouteOption(BaseModel):
    id: str
    label: str
    distance_m: int
    duration_s: int
    polyline: str
    sensory: SensoryResult
    # US 1.3 — set only when the request included sensitivity_threshold;
    # None (not False) when no preference was given, so the frontend can
    # tell "definitely within your comfort level" apart from "no preference
    # was expressed at all".
    exceeds_threshold: bool | None = None
    # Turn-by-turn navigation steps. Empty list, not None, when a provider
    # returns none — RouteCard/navigation UI can treat [] as "no steps to
    # show" without a separate null check.
    steps: list[RouteStep] = Field(default_factory=list)


class RouteResponse(BaseModel):
    routes: list[RouteOption]
    generated_at: str
    # True only when every returned route exceeds the requested threshold —
    # the "no fully comfortable route available" case from the DoD ("route
    # recommendations dynamically adjust when crowd levels exceed
    # user-defined limits"). The frontend should still show routes (best
    # available, already sorted calmest-first), just with a clear notice.
    all_routes_exceed_threshold: bool = False


class QuietSpace(BaseModel):
    id: str
    name: str
    type: str
    category: RefugeCategory
    lat: float
    lng: float
    distance_m: int
    # Static, hand-written — not live occupancy or noise data.
    # TODO(US2.2): a real "quiet now" status needs the pedestrian sensor
    # join described in data/README.md; don't compute one from this field.
    description: str


class QuietSpaceQuery(BaseModel):
    """Framework-independent validation for quiet-space URL parameters."""

    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    radius_m: int = Field(500, ge=100, le=5000)
    limit: int = Field(5, ge=1, le=20)
    category: RefugeCategory | None = None


class QuietSpaceResponse(BaseModel):
    quiet_spaces: list[QuietSpace]
    radius_m: int
    message: str | None = None


class RefugeDetourRequest(BaseModel):
    """AC5: detour to a refuge and back onto the original route."""

    current: Coordinate
    refuge: Coordinate
    destination: Coordinate


class RefugeLeg(BaseModel):
    name: str
    distance_m: int
    duration_s: int
    polyline: str
    sensory: SensoryResult


class RefugeDetourResponse(BaseModel):
    legs: list[RefugeLeg]
    total_distance_m: int
    total_duration_s: int
    generated_at: str


class PredictiveAlert(BaseModel):
    """US 2.2 — an area whose last 3 readings are strictly rising, not just
    currently busy. percent_increase compares the latest reading to the one
    immediately before it."""

    id: str
    name: str
    lat: float
    lng: float
    percent_increase: float
    message: str


class PredictiveAlertsResponse(BaseModel):
    alerts: list[PredictiveAlert]
    generated_at: str
