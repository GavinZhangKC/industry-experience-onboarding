import json

import pytest

from app.errors import DataUnavailable
from app.lib.aurora_data_store import AuroraDataStore, _weight_from_reading


class FakeRDSDataClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def execute_statement(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return {"formattedRecords": json.dumps(response)}


def _store(client):
    return AuroraDataStore(
        region="ap-southeast-2",
        cluster_arn="cluster-arn",
        secret_arn="secret-arn",
        database="postgres",
        client=client,
    )


@pytest.mark.parametrize(
    ("count", "average", "expected"),
    [
        (50, 100, 1),
        (90, 100, 2),
        (110, 100, 3),
        (140, 100, 4),
        (160, 100, 5),
        (100, None, 1),
    ],
)
def test_weight_from_live_reading(count, average, expected):
    assert _weight_from_reading(count, average) == expected


def test_busy_areas_match_existing_scoring_contract():
    client = FakeRDSDataClient(
        [
            [
                {
                    "id": "sensor-1",
                    "name": "Flinders Street",
                    "type": "pedestrian_sensor",
                    "lat": -37.8183,
                    "lng": 144.9671,
                    "current_count": 160,
                    "rolling_avg_4wk": 100.0,
                }
            ]
        ]
    )
    store = _store(client)

    assert store.busy_areas == [
        {
            "id": "sensor-1",
            "name": "Flinders Street",
            "type": "pedestrian_sensor",
            "lat": -37.8183,
            "lng": 144.9671,
            "weight": 5,
        }
    ]
    assert len(client.calls) == 1
    assert client.calls[0]["formatRecordsAs"] == "JSON"


def test_quiet_spaces_match_existing_refuge_contract():
    client = FakeRDSDataClient(
        [
            [
                {
                    "id": "refuge-1",
                    "name": "City Library",
                    "type": "indoor",
                    "lat": -37.8163,
                    "lng": 144.9670,
                }
            ]
        ]
    )

    assert _store(client).quiet_spaces == [
        {
            "id": "refuge-1",
            "name": "City Library",
            "type": "indoor",
            "lat": -37.8163,
            "lng": 144.967,
        }
    ]


def test_database_error_is_converted_to_data_unavailable():
    store = _store(FakeRDSDataClient([RuntimeError("database detail")]))

    with pytest.raises(DataUnavailable) as exc_info:
        _ = store.quiet_spaces

    assert "database detail" not in exc_info.value.message


def test_aurora_configuration_is_required():
    with pytest.raises(DataUnavailable):
        AuroraDataStore(
            region="ap-southeast-2",
            cluster_arn="",
            secret_arn="",
            database="postgres",
            client=FakeRDSDataClient([]),
        )
