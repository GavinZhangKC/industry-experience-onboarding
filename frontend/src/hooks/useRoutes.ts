import { useCallback, useEffect, useRef, useState } from "react";
import { planRoutes } from "../api/routes";
import { ApiError, type Coordinate, type RouteOption } from "../api/types";

interface RoutesState {
  routes: RouteOption[] | null;
  loading: boolean;
  error: ApiError | null;
}

export function useRoutes() {
  const [state, setState] = useState<RoutesState>({ routes: null, loading: false, error: null });
  const activeRequest = useRef<AbortController | null>(null);

  const search = useCallback(async (origin: Coordinate, destination: Coordinate) => {
    activeRequest.current?.abort();
    const controller = new AbortController();
    activeRequest.current = controller;
    setState({ routes: null, loading: true, error: null });
    try {
      const response = await planRoutes(origin, destination, 3, controller.signal);
      if (activeRequest.current !== controller) return;
      setState({ routes: response.routes, loading: false, error: null });
    } catch (err) {
      if (controller.signal.aborted || activeRequest.current !== controller) return;
      const apiError =
        err instanceof ApiError
          ? err
          : new ApiError({ code: "internal_error", message: "Something went wrong on our side.", request_id: null });
      setState({ routes: null, loading: false, error: apiError });
    } finally {
      if (activeRequest.current === controller) activeRequest.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    activeRequest.current?.abort();
    activeRequest.current = null;
    setState({ routes: null, loading: false, error: null });
  }, []);

  useEffect(() => () => activeRequest.current?.abort(), []);

  return { ...state, search, reset };
}
