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


class RouteOption(BaseModel):
    id: str
    label: str
    distance_m: int
    duration_s: int
    polyline: str
    sensory: SensoryResult


class RouteResponse(BaseModel):
    routes: list[RouteOption]
    generated_at: str


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
