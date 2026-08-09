import type { RouteOption } from "../../api/types";
import { SensoryBadge } from "./SensoryBadge";
import styles from "./RouteCard.module.css";

interface RouteCardProps {
  route: RouteOption;
  isSelected: boolean;
  onSelect: () => void;
}

function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60);
  return `${minutes} min`;
}

function formatDistance(metres: number): string {
  if (metres >= 1000) {
    return `${(metres / 1000).toFixed(1)} km`;
  }
  return `${metres} m`;
}

export function RouteCard({ route, isSelected, onSelect }: RouteCardProps) {
  return (
    <li>
      <button type="button" className={styles.card} aria-pressed={isSelected} onClick={onSelect}>
        <div className={styles.headerRow}>
          <span className={styles.label}>
            {route.label}
            {isSelected && <span className={styles.selectedTag}> — Selected</span>}
          </span>
          <span className={styles.metrics}>
            {formatDuration(route.duration_s)} · {formatDistance(route.distance_m)}
          </span>
        </div>
        <SensoryBadge level={route.sensory.level} score={route.sensory.score} />
        <p className={styles.explanation}>{route.sensory.explanation}</p>
      </button>
    </li>
  );
}
