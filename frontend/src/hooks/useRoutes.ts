import { useCallback, useState } from "react";
import { planRoutes } from "../api/routes";
import { ApiError, type Coordinate, type RouteOption } from "../api/types";

interface RoutesState {
  routes: RouteOption[] | null;
  loading: boolean;
  error: ApiError | null;
}

export function useRoutes() {
  const [state, setState] = useState<RoutesState>({ routes: null, loading: false, error: null });

  const search = useCallback(async (origin: Coordinate, destination: Coordinate) => {
    setState({ routes: null, loading: true, error: null });
    try {
      const response = await planRoutes(origin, destination);
      setState({ routes: response.routes, loading: false, error: null });
    } catch (err) {
      const apiError =
        err instanceof ApiError
          ? err
          : new ApiError({ code: "internal_error", message: "Something went wrong on our side.", request_id: null });
      setState({ routes: null, loading: false, error: apiError });
    }
  }, []);

  const reset = useCallback(() => setState({ routes: null, loading: false, error: null }), []);

  return { ...state, search, reset };
}
