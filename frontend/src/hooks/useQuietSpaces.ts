import { useCallback, useState } from "react";
import { findQuietSpaces } from "../api/quietSpaces";
import { ApiError, type Coordinate, type QuietSpaceResponse } from "../api/types";

export const RADIUS_STEPS_M = [500, 1000, 2000] as const;

interface QuietSpacesState {
  data: QuietSpaceResponse | null;
  loading: boolean;
  error: ApiError | null;
  center: Coordinate | null;
}

export function useQuietSpaces() {
  const [state, setState] = useState<QuietSpacesState>({
    data: null,
    loading: false,
    error: null,
    center: null,
  });

  const search = useCallback(async (center: Coordinate, radiusM: number = RADIUS_STEPS_M[0]) => {
    setState((prev) => ({ ...prev, loading: true, error: null, center }));
    try {
      const data = await findQuietSpaces(center.lat, center.lng, radiusM);
      setState({ data, loading: false, error: null, center });
    } catch (err) {
      const apiError =
        err instanceof ApiError
          ? err
          : new ApiError({ code: "internal_error", message: "Something went wrong on our side.", request_id: null });
      setState({ data: null, loading: false, error: apiError, center });
    }
  }, []);

  const expandRadius = useCallback(() => {
    if (!state.center || !state.data) return;
    const currentIndex = RADIUS_STEPS_M.indexOf(state.data.radius_m as (typeof RADIUS_STEPS_M)[number]);
    const nextRadius = RADIUS_STEPS_M[currentIndex + 1];
    if (nextRadius === undefined) return;
    search(state.center, nextRadius);
  }, [state.center, state.data, search]);

  const canExpand =
    state.data !== null &&
    RADIUS_STEPS_M.indexOf(state.data.radius_m as (typeof RADIUS_STEPS_M)[number]) < RADIUS_STEPS_M.length - 1;

  const reset = useCallback(() => setState({ data: null, loading: false, error: null, center: null }), []);

  return { ...state, search, expandRadius, canExpand, reset };
}
