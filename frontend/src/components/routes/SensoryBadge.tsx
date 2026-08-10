import type { SensoryLevel } from "../../api/types";
import { SENSORY_LEVEL_PRESENTATION } from "../../constants/sensory";
import styles from "./SensoryBadge.module.css";

interface SensoryBadgeProps {
  level: SensoryLevel;
  score: number;
}

const LEVEL_CLASS: Record<SensoryLevel, string> = {
  low: styles.low,
  medium: styles.medium,
  high: styles.high,
};

export function SensoryBadge({
  level,
  score,
}: SensoryBadgeProps) {
  const presentation =
    SENSORY_LEVEL_PRESENTATION[level];

  return (
    <span className={styles.badge}>
      <span
        className={`${styles.glyph} ${LEVEL_CLASS[level]}`}
        aria-hidden="true"
      >
        {presentation.glyph}
      </span>

      <span>
        {presentation.label} sensory load — {score}/100
      </span>
    </span>
  );
}
