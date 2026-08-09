import type { SensoryLevel } from "../../api/types";
import { SENSORY_LEVEL_PRESENTATION } from "../../constants/sensory";
import styles from "./SensoryBadge.module.css";

const LEVEL_VAR: Record<SensoryLevel, string> = {
  low: "var(--color-sensory-low)",
  medium: "var(--color-sensory-medium)",
  high: "var(--color-sensory-high)",
};

interface SensoryBadgeProps {
  level: SensoryLevel;
  score: number;
}

// Level is never colour-only: the glyph shape (circle/triangle/square) and
// the text label both carry the same information as the colour.
export function SensoryBadge({ level, score }: SensoryBadgeProps) {
  const presentation = SENSORY_LEVEL_PRESENTATION[level];
  return (
    <span className={styles.badge}>
      <span className={styles.glyph} style={{ background: LEVEL_VAR[level] }} aria-hidden="true">
        {presentation.glyph}
      </span>
      {presentation.label} sensory load — {score}/100
    </span>
  );
}
