"""Pure geometry helpers. No framework imports, no I/O — trivially testable."""

import math

EARTH_RADIUS_M = 6_371_000.0

Point = tuple[float, float]  # (lat, lng)


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def decode_polyline(encoded: str) -> list[Point]:
    """Decode a Google encoded polyline into (lat, lng) pairs."""
    points: list[Point] = []
    index = lat = lng = 0
    length = len(encoded)

    while index < length:
        for is_lat in (True, False):
            shift = result = 0
            while True:
                if index >= length:
                    raise ValueError("encoded polyline ended mid-coordinate")
                byte = ord(encoded[index]) - 63
                index += 1
                if byte < 0 or byte > 0x3F:
                    raise ValueError("encoded polyline contains an invalid character")
                result |= (byte & 0x1F) << shift
                shift += 5
                if shift > 60:
                    raise ValueError("encoded polyline coordinate is too large")
                if byte < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else (result >> 1)
            if is_lat:
                lat += delta
            else:
                lng += delta
        points.append((lat / 1e5, lng / 1e5))
    return points


def encode_polyline(points: list[Point]) -> str:
    """Encode (lat, lng) pairs into a Google encoded polyline.

    Only needed by the mock mapping client, so the frontend receives the same
    shape of data it will get from the real provider.
    """

    def _chunk(value: int) -> str:
        value = ~(value << 1) if value < 0 else (value << 1)
        out = ""
        while value >= 0x20:
            out += chr((0x20 | (value & 0x1F)) + 63)
            value >>= 5
        return out + chr(value + 63)

    result = ""
    prev_lat = prev_lng = 0
    for lat, lng in points:
        ilat, ilng = round(lat * 1e5), round(lng * 1e5)
        result += _chunk(ilat - prev_lat) + _chunk(ilng - prev_lng)
        prev_lat, prev_lng = ilat, ilng
    return result


def _project(lat: float, lng: float, lat0: float) -> tuple[float, float]:
    """Equirectangular projection to local metres. Accurate enough over a few
    kilometres, which is all a CBD walking route covers."""
    x = math.radians(lng) * math.cos(math.radians(lat0)) * EARTH_RADIUS_M
    y = math.radians(lat) * EARTH_RADIUS_M
    return x, y


def distance_point_to_path_m(lat: float, lng: float, path: list[Point]) -> float:
    """Shortest distance from a point to a polyline, in metres.

    Measures against each SEGMENT rather than each vertex, so a busy area
    sitting between two widely spaced vertices is not missed.
    """
    if not path:
        return float("inf")
    if len(path) == 1:
        return haversine_m(lat, lng, path[0][0], path[0][1])

    lat0 = path[0][0]
    px, py = _project(lat, lng, lat0)
    best = float("inf")

    for (alat, alng), (blat, blng) in zip(path, path[1:]):
        ax, ay = _project(alat, alng, lat0)
        bx, by = _project(blat, blng, lat0)
        dx, dy = bx - ax, by - ay
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            t = 0.0
        else:
            t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
        cx, cy = ax + t * dx, ay + t * dy
        best = min(best, math.hypot(px - cx, py - cy))

    return best
