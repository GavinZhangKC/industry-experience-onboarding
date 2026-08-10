import { apiPost } from "./client";
import type { Coordinate, RouteResponse } from "./types";

export function planRoutes(
  origin: Coordinate,
  destination: Coordinate,
  alternatives = 3,
  signal?: AbortSignal,
): Promise<RouteResponse> {
  return apiPost<RouteResponse>("/api/v1/routes", {
    origin,
    destination,
    alternatives,
  }, { signal });
}
