import { useCallback, useState } from "react";
import type { Coordinate } from "../api/types";

interface GeolocationState {
  loading: boolean;
  error: string | null;
}

// Deliberately does not cache or persist the resolved position anywhere
// (no state beyond this call) — origin/destination/current-location data
// must never be written to localStorage or similar.
export function useGeolocation() {
  const [state, setState] = useState<GeolocationState>({ loading: false, error: null });

  const getCurrentPosition = useCallback((): Promise<Coordinate> => {
    setState({ loading: true, error: null });
    return new Promise((resolve, reject) => {
      if (!("geolocation" in navigator)) {
        const message = "Location isn't available in this browser.";
        setState({ loading: false, error: message });
        reject(new Error(message));
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setState({ loading: false, error: null });
          resolve({ lat: position.coords.latitude, lng: position.coords.longitude });
        },
        (err) => {
          const message =
            err.code === err.PERMISSION_DENIED
              ? "Location access was denied. Pick a point on the map instead."
              : "Couldn't determine your location. Pick a point on the map instead.";
          setState({ loading: false, error: message });
          reject(new Error(message));
        },
        { enableHighAccuracy: false, timeout: 8000 },
      );
    });
  }, []);

  return { ...state, getCurrentPosition };
}
