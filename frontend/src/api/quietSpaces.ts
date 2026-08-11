import { apiGet } from "./client";
import type { QuietSpaceResponse } from "./types";

export type RefugeCategory = "green_space" | "indoor";

export function findQuietSpaces(
  lat: number,
  lng: number,
  radiusM = 500,
  limit = 5,
  category?: RefugeCategory,
  signal?: AbortSignal,
): Promise<QuietSpaceResponse> {
  const params = new URLSearchParams({
    lat: String(lat),
    lng: String(lng),
    radius_m: String(radiusM),
    limit: String(limit),
  });

  if (category) {
    params.set("category", category);
  }

  return apiGet<QuietSpaceResponse>(
    `/api/v1/quiet-spaces?${params.toString()}`,
    { signal },
  );
}