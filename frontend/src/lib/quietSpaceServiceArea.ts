import type { Coordinate } from "../api/types";

export const QUIET_SPACE_CBD_CENTER: Coordinate = { lat: -37.8136, lng: 144.9631 };
export const QUIET_SPACE_CBD_RADIUS_M = 5_000;

function degreesToRadians(value: number): number {
  return (value * Math.PI) / 180;
}

function distanceMetres(from: Coordinate, to: Coordinate): number {
  const earthRadiusM = 6_371_000;
  const fromLat = degreesToRadians(from.lat);
  const toLat = degreesToRadians(to.lat);
  const deltaLat = degreesToRadians(to.lat - from.lat);
  const deltaLng = degreesToRadians(to.lng - from.lng);

  const a =
    Math.sin(deltaLat / 2) ** 2 +
    Math.cos(fromLat) * Math.cos(toLat) * Math.sin(deltaLng / 2) ** 2;

  return earthRadiusM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function isWithinQuietSpaceServiceArea(coordinate: Coordinate): boolean {
  return distanceMetres(coordinate, QUIET_SPACE_CBD_CENTER) <= QUIET_SPACE_CBD_RADIUS_M;
}
