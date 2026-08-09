"""Read-only Aurora/PostGIS adapter for the existing service data contract."""

import json
import logging
from functools import lru_cache
from typing import Any, Protocol

from app.errors import DataUnavailable

logger = logging.getLogger(__name__)


class RDSDataClient(Protocol):
    def execute_statement(self, **kwargs) -> dict[str, Any]: ...


BUSY_AREAS_SQL = """
SELECT
    ps.sensor_id AS id,
    l.name,
    'pedestrian_sensor' AS type,
    ST_Y(l.geom) AS lat,
    ST_X(l.geom) AS lng,
    latest.count AS current_count,
    latest.rolling_avg_4wk
FROM pedestrian_sensor ps
JOIN location l ON l.location_id = ps.location_id
JOIN LATERAL (
    SELECT pr.count, pr.rolling_avg_4wk
    FROM pedestrian_reading pr
    WHERE pr.sensor_id = ps.sensor_id
    ORDER BY pr.recorded_at DESC NULLS LAST, pr.fetched_at DESC
    LIMIT 1
) latest ON TRUE
WHERE LOWER(COALESCE(ps.status, '')) NOT IN ('i', 'inactive')
"""

QUIET_SPACES_SQL = """
SELECT
    r.refuge_id::text AS id,
    COALESCE(r.name, l.name) AS name,
    COALESCE(r.type, 'quiet_space') AS type,
    ST_Y(l.geom) AS lat,
    ST_X(l.geom) AS lng
FROM refuge r
JOIN location l ON l.location_id = r.location_id
"""


def _weight_from_reading(count: int | float, rolling_average: int | float | None) -> int:
    """Bridge live readings to the 1-5 weight expected by the F2 scorer.

    The database ingestion already defines sensory load as current pedestrian
    volume relative to its four-week average. Five bands preserve that signal
    while keeping the existing F2 scoring contract unchanged.
    """
    if rolling_average is None or rolling_average <= 0:
        return 1
    ratio = count / rolling_average
    if ratio <= 0.75:
        return 1
    if ratio <= 1.0:
        return 2
    if ratio <= 1.25:
        return 3
    if ratio <= 1.5:
        return 4
    return 5


class AuroraDataStore:
    def __init__(
        self,
        *,
        region: str,
        cluster_arn: str,
        secret_arn: str,
        database: str,
        client: RDSDataClient | None = None,
    ):
        if not cluster_arn or not secret_arn:
            raise DataUnavailable(
                "Aurora is selected but its connection configuration is missing."
            )
        self._cluster_arn = cluster_arn
        self._secret_arn = secret_arn
        self._database = database
        self._client = client or _create_client(region)

    def _select(self, sql: str) -> list[dict[str, Any]]:
        try:
            response = self._client.execute_statement(
                resourceArn=self._cluster_arn,
                secretArn=self._secret_arn,
                database=self._database,
                sql=sql,
                formatRecordsAs="JSON",
            )
            records = json.loads(response.get("formattedRecords", "[]"))
            if not isinstance(records, list):
                raise ValueError("Aurora result was not a JSON array")
            return records
        except Exception as exc:
            logger.exception("Aurora reference-data query failed")
            raise DataUnavailable(
                "Reference data could not be loaded from Aurora."
            ) from exc

    @property
    def busy_areas(self) -> list[dict]:
        records = self._select(BUSY_AREAS_SQL)
        return [
            {
                "id": str(record["id"]),
                "name": str(record["name"]),
                "type": str(record["type"]),
                "lat": float(record["lat"]),
                "lng": float(record["lng"]),
                "weight": _weight_from_reading(
                    float(record["current_count"]),
                    None
                    if record.get("rolling_avg_4wk") is None
                    else float(record["rolling_avg_4wk"]),
                ),
            }
            for record in records
        ]

    @property
    def quiet_spaces(self) -> list[dict]:
        records = self._select(QUIET_SPACES_SQL)
        return [
            {
                "id": str(record["id"]),
                "name": str(record["name"]),
                "type": str(record["type"]),
                "lat": float(record["lat"]),
                "lng": float(record["lng"]),
            }
            for record in records
        ]


def _create_client(region: str) -> RDSDataClient:
    try:
        import boto3
    except ImportError as exc:
        raise DataUnavailable(
            "The AWS SDK is required when DATA_BACKEND=aurora."
        ) from exc
    return boto3.client("rds-data", region_name=region)


@lru_cache
def get_aurora_data_store(
    *, region: str, cluster_arn: str, secret_arn: str, database: str
) -> AuroraDataStore:
    return AuroraDataStore(
        region=region,
        cluster_arn=cluster_arn,
        secret_arn=secret_arn,
        database=database,
    )
