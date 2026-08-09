import polyline from "@mapbox/polyline";
import type { LatLngTuple } from "leaflet";

export function decodePolyline(encoded: string): LatLngTuple[] {
  return polyline.decode(encoded) as LatLngTuple[];
}
