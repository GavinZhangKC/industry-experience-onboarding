"""BE-F4: load and validate the prepared reference datasets.

Deliberately file-backed for the MVP. Every record has the same four required
fields, so swapping this for Supabase or Postgres later means rewriting one
class and nothing else.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path

from app.errors import DataUnavailable

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ("id", "name", "type", "lat", "lng")


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

    def reload(self) -> None:
        self._busy_areas = None
        self._quiet_spaces = None


@lru_cache
def get_data_store(data_dir: str = "data") -> DataStore:
    return DataStore(data_dir)
