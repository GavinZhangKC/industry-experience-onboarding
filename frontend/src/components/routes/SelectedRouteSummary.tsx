import type { RouteOption } from "../../api/types";
import { SENSORY_LEVEL_PRESENTATION } from "../../constants/sensory";
import styles from "./SelectedRouteSummary.module.css";

interface SelectedRouteSummaryProps {
  route: RouteOption;
  onExit: () => void;
}

function formatDuration(seconds: number) {
  return `${Math.max(1, Math.round(seconds / 60))} min`;
}

function formatDistance(metres: number) {
  if (metres < 1000) {
    return `${Math.round(metres)} m`;
  }

  return `${(metres / 1000).toFixed(1)} km`;
}

export function SelectedRouteSummary({
  route,
  onExit,
}: SelectedRouteSummaryProps) {
  const presentation =
    SENSORY_LEVEL_PRESENTATION[route.sensory.level];

  return (
    <aside
      className={styles.card}
      aria-label={`Selected route: ${route.label}`}
    >
      <div className={styles.heading}>
        <strong>{route.label}</strong>

        <span>
          {formatDuration(route.duration_s)} ·{" "}
          {formatDistance(route.distance_m)}
        </span>
      </div>

      <div
        className={`${styles.level} ${
          styles[route.sensory.level]
        }`}
      >
        <span aria-hidden="true">
          {presentation.glyph}
        </span>

        {presentation.label} sensory load
      </div>

      <dl className={styles.details}>
        <div>
          <dt>Sensory score</dt>
          <dd>{route.sensory.score}/100</dd>
        </div>
      </dl>

      <p className={styles.explanation}>
        {route.sensory.explanation}
      </p>

      <button
        type="button"
        className={styles.exitButton}
        onClick={onExit}
      >
        Exit route
      </button>
    </aside>
  );
}