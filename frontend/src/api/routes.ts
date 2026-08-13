import { apiGet, apiPost } from "./client";
import type { Coordinate, PredictiveAlertsResponse, RouteResponse } from "./types";

export function planRoutes(
  origin: Coordinate,
  destination: Coordinate,
  alternatives = 3,
  signal?: AbortSignal,
  sensitivityThreshold?: number,
): Promise<RouteResponse> {
  return apiPost<RouteResponse>("/api/v1/routes", {
    origin,
    destination,
    alternatives,
    ...(sensitivityThreshold !== undefined && { sensitivity_threshold: sensitivityThreshold }),
  }, { signal });
}

export function getPredictiveAlerts(signal?: AbortSignal): Promise<PredictiveAlertsResponse> {
  return apiGet<PredictiveAlertsResponse>("/api/v1/predictive-alerts", { signal });
}
