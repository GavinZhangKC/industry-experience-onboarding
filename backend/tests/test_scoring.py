from app.lib.geo import encode_polyline, decode_polyline
from app.services.scoring_service import score_route

BUSY = [
    {"id": "a", "name": "Busy Corner", "type": "intersection", "lat": -37.8150, "lng": 144.9600, "weight": 5},
    {"id": "b", "name": "Second Corner", "type": "intersection", "lat": -37.8140, "lng": 144.9600, "weight": 4},
]

KW = {"proximity_m": 120.0, "low_threshold": 33, "medium_threshold": 66}


def _path(points):
    return decode_polyline(encode_polyline(points))


def test_clear_route_scores_low_and_says_so():
    path = _path([(-37.8300, 144.9800), (-37.8320, 144.9820)])
    result = score_route(path, BUSY, **KW)
    assert result.score == 0
    assert result.level == "low"
    assert result.factors == []
    assert "clear" in result.explanation.lower()


def test_route_through_busy_areas_scores_higher():
    path = _path([(-37.8160, 144.9600), (-37.8130, 144.9600)])
    result = score_route(path, BUSY, **KW)
    assert result.score > 0
    assert len(result.factors) == 2


def test_label_and_explanation_never_contradict():
    """US1.1 AC4: the level and the explanation come from one set of findings."""
    path = _path([(-37.8160, 144.9600), (-37.8130, 144.9600)])
    result = score_route(path, BUSY, **KW)

    if result.factors:
        assert "clear" not in result.explanation.lower()
        for factor in result.factors[:2]:
            assert factor.name in result.explanation
    else:
        assert result.level == "low"


def test_score_is_capped_at_100():
    many = [dict(BUSY[0], id=str(i), name=f"Corner {i}") for i in range(50)]
    path = _path([(-37.8155, 144.9600), (-37.8145, 144.9600)])
    result = score_route(path, many, **KW)
    assert result.score == 100
    assert result.level == "high"
