// Mirrors backend/app/schemas.py and backend/app/errors.py exactly.
// Do not add fields the backend doesn't send, and do not invent endpoints.

export interface Coordinate {
  lat: number;
  lng: number;
}

export type SensoryLevel = "low" | "medium" | "high";

export interface SensoryFactor {
  name: string;
  type: string;
  distance_m: number;
  weight: number;
}

export interface SensoryResult {
  score: number;
  level: SensoryLevel;
  explanation: string;
  factors: SensoryFactor[];
}

export interface RouteOption {
  id: string;
  label: string;
  distance_m: number;
  duration_s: number;
  polyline: string;
  sensory: SensoryResult;
}

export interface RouteRequest {
  origin: Coordinate;
  destination: Coordinate;
  alternatives?: number;
}

export interface RouteResponse {
  routes: RouteOption[];
  generated_at: string;
}

export interface QuietSpace {
  id: string;
  name: string;
  type: string;
  lat: number;
  lng: number;
  distance_m: number;
}

export interface QuietSpaceResponse {
  quiet_spaces: QuietSpace[];
  radius_m: number;
  message: string | null;
}

export interface HealthResponse {
  status: string;
  maps_provider: string;
  busy_areas: number;
  quiet_spaces: number;
}

// The stable, machine-readable codes from backend/app/errors.py. Switch on
// these, never on the message text.
export type ApiErrorCode =
  | "invalid_request"
  | "out_of_service_area"
  | "no_routes_found"
  | "upstream_error"
  | "data_unavailable"
  | "rate_limited"
  | "internal_error";

export interface ApiErrorBody {
  error: {
    code: ApiErrorCode;
    message: string;
    request_id: string | null;
    details?: unknown;
  };
}

export class ApiError extends Error {
  code: ApiErrorCode;
  requestId: string | null;

  constructor(body: ApiErrorBody["error"]) {
    super(body.message);
    this.code = body.code;
    this.requestId = body.request_id;
  }
}
