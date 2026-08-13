"""Reference-data contract and local JSON implementation.

Services depend on ``ReferenceDataStore`` rather than a storage technology.
Local development uses JSON; AWS can select the Aurora adapter with settings.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from app.errors import DataUnavailable

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ("id", "name", "type", "lat", "lng")


class ReferenceDataStore(Protocol):
    """The read contract consumed by F1/F2 and F3 services."""

    @property
    def busy_areas(self) -> list[dict]: ...

    @property
    def quiet_spaces(self) -> list[dict]: ...

    @property
    def trending_areas(self) -> list[dict]:
        """Areas whose last 3 readings are strictly increasing — a genuine
        upward trend, not just "currently busy". Backs US 2.2's predictive
        alerts. Optional: implementations may return [] rather than raise,
        since a lack of trend data shouldn't break routing or quiet-space
        search, which don't depend on this."""
        ...


def _load(path: Path, extra_required: tuple[str, ...] = ()) -> list[dict]:
    if not path.exists():
        raise DataUnavailable(f"Reference dataset missing: {path.name}")
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataUnavailable(f"Reference dataset {path.name} is not valid JSON") from exc

    if not isinstance(records, list):
        raise DataUnavailable(f"Reference dataset {path.name} must be a JSON array")

    required = REQUIRED_FIELDS + extra_required
    for i, record in enumerate(records):
        missing = [f for f in required if f not in record]
        if missing:
            raise DataUnavailable(
                f"{path.name} record {i} is missing required fields: {', '.join(missing)}"
            )
    return records


class DataStore:
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self._busy_areas: list[dict] | None = None
        self._quiet_spaces: list[dict] | None = None
        self._trending_areas: list[dict] | None = None

    @property
    def busy_areas(self) -> list[dict]:
        if self._busy_areas is None:
            self._busy_areas = _load(self.data_dir / "busy_areas.json", ("weight",))
            logger.info("Loaded %d busy areas", len(self._busy_areas))
        return self._busy_areas

    @property
    def quiet_spaces(self) -> list[dict]:
        if self._quiet_spaces is None:
            self._quiet_spaces = _load(self.data_dir / "quiet_spaces.json", ("description",))
            logger.info("Loaded %d quiet spaces", len(self._quiet_spaces))
        return self._quiet_spaces

    @property
    def trending_areas(self) -> list[dict]:
        # Optional file — mock mode works fine with no predictive alerts at
        # all (an empty list), since this feature depends on real historical
        # data that a static JSON fixture can't meaningfully simulate.
        if self._trending_areas is None:
            path = self.data_dir / "trending_areas.json"
            self._trending_areas = _load(path, ("latest", "prev", "percent_increase")) if path.exists() else []
            logger.info("Loaded %d trending areas", len(self._trending_areas))
        return self._trending_areas

    def reload(self) -> None:
        self._busy_areas = None
        self._quiet_spaces = None
        self._trending_areas = None


@lru_cache
def get_data_store(data_dir: str = "data") -> DataStore:
    return DataStore(data_dir)


def get_configured_data_store(settings: "Settings") -> ReferenceDataStore:
    """Select local JSON or Aurora without leaking that choice into services."""
    if settings.data_backend == "aurora":
        from app.lib.aurora_data_store import get_aurora_data_store

        return get_aurora_data_store(
            region=settings.aws_region,
            cluster_arn=settings.db_cluster_arn,
            secret_arn=settings.db_secret_arn,
            database=settings.db_name,
        )
    return get_data_store(settings.data_dir)
