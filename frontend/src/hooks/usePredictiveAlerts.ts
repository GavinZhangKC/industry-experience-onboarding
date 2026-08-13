import { useCallback, useEffect, useRef, useState } from "react";
import { getPredictiveAlerts } from "../api/routes";
import { ApiError, type PredictiveAlert } from "../api/types";

interface PredictiveAlertsState {
  alerts: PredictiveAlert[];
  loading: boolean;
  error: ApiError | null;
}

export function usePredictiveAlerts() {
  const [state, setState] = useState<PredictiveAlertsState>({
    alerts: [],
    loading: false,
    error: null,
  });
  const activeRequest = useRef<AbortController | null>(null);

  const fetchAlerts = useCallback(async () => {
    activeRequest.current?.abort();
    const controller = new AbortController();
    activeRequest.current = controller;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await getPredictiveAlerts(controller.signal);
      if (activeRequest.current !== controller) return;
      setState({ alerts: response.alerts, loading: false, error: null });
    } catch (err) {
      if (controller.signal.aborted || activeRequest.current !== controller) return;
      const apiError =
        err instanceof ApiError
          ? err
          : new ApiError({ code: "internal_error", message: "Couldn't load predictive alerts.", request_id: null });
      setState({ alerts: [], loading: false, error: apiError });
    } finally {
      if (activeRequest.current === controller) activeRequest.current = null;
    }
  }, []);

  useEffect(() => () => activeRequest.current?.abort(), []);

  return { ...state, fetchAlerts };
}
