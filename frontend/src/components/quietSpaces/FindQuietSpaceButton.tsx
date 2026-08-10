import type { Coordinate } from "../../api/types";
import { useGeolocation } from "../../hooks/useGeolocation";
import { Button } from "../common/Button";
import styles from "./FindQuietSpaceButton.module.css";

interface FindQuietSpaceButtonProps {
  mapCenter: Coordinate;
  onFind: (center: Coordinate, note: string | null) => void;
}

// Always visible, one click away from any screen (this is the one required
// interaction; geolocation permission, if prompted, is the browser's UI, not
// ours). Tries the user's real location first and falls back to the current
// map centre so the feature never dead-ends.
export function FindQuietSpaceButton({ mapCenter, onFind }: FindQuietSpaceButtonProps) {
  const { loading, getCurrentPosition } = useGeolocation();

  const handleClick = async () => {
    try {
      const position = await getCurrentPosition();
      onFind(position, null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Couldn't determine your location.";
      onFind(mapCenter, `${message} Showing quiet spaces near the map centre instead.`);
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
        Uses your location, or the map centre if unavailable.
      </span>
    </div>
  );
}
