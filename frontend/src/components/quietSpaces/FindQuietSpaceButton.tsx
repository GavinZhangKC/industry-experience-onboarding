import type { Coordinate } from "../../api/types";
import { useGeolocation } from "../../hooks/useGeolocation";
import { isWithinQuietSpaceServiceArea } from "../../lib/quietSpaceServiceArea";
import { Button } from "../common/Button";
import styles from "./FindQuietSpaceButton.module.css";

interface FindQuietSpaceButtonProps {
  onFind: (center: Coordinate, note: string | null) => void;
  onPickOnMap: (message: string) => void;
}

// Always visible, one click away from any screen (this is the one required
// interaction; geolocation permission, if prompted, is the browser's UI, not
// ours). Locations outside the CBD data coverage switch to explicit map
// selection instead of silently searching around an unrelated coordinate.
export function FindQuietSpaceButton({ onFind, onPickOnMap }: FindQuietSpaceButtonProps) {
  const { loading, getCurrentPosition } = useGeolocation();

  const handleClick = async () => {
    try {
      const position = await getCurrentPosition();
      if (isWithinQuietSpaceServiceArea(position)) {
        onFind(position, "Using your current location.");
        return;
      }
      onPickOnMap(
        "Your current location is outside the Melbourne CBD search area. Click a point on the CBD map to search there.",
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Couldn't determine your location.";
      onPickOnMap(`${message} Click a point on the CBD map to search there.`);
    }
  };

  return (
    <div className={styles.wrapper}>
      <Button
        type="button"
        className={styles.button}
        onClick={handleClick}
        disabled={loading}
      >
        {loading
          ? "Finding your location…"
          : "Find quiet space"}
      </Button>

      <span className={styles.status}>
        Uses your location in the CBD, or lets you choose a point on the map.
      </span>
    </div>
  );
}
