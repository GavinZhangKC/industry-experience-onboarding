import { apiGet } from "./client";
import type { QuietSpaceResponse } from "./types";

export function findQuietSpaces(
  lat: number,
  lng: number,
  radiusM = 500,
  limit = 5,
): Promise<QuietSpaceResponse> {
  const params = new URLSearchParams({
    lat: String(lat),
    lng: String(lng),
    radius_m: String(radiusM),
    limit: String(limit),
  });
  return apiGet<QuietSpaceResponse>(`/api/v1/quiet-spaces?${params}`);
}
