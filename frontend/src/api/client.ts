import { ApiError, type ApiErrorBody } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    // Network failure: the backend never returns this shape for a request
    // that reached it, so it's synthesized here to keep the caller's error
    // handling uniform.
    throw new ApiError({
      code: "upstream_error",
      message: "Could not reach the server. Check your connection and try again.",
      request_id: null,
    });
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await response.json();
    } catch {
      // fall through to generic error below
    }
    if (body?.error) {
      throw new ApiError(body.error);
    }
    throw new ApiError({
      code: "internal_error",
      message: "Something went wrong on our side.",
      request_id: null,
    });
  }

  return response.json() as Promise<T>;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}
