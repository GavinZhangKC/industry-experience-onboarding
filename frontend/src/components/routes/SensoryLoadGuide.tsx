import type { SensoryLevel } from "../../api/types";
import { SENSORY_LEVEL_PRESENTATION } from "../../constants/sensory";
import styles from "./SensoryLoadGuide.module.css";

interface SensoryLoadGuideProps {
  compact?: boolean;
}

const GUIDE_ITEMS: Array<{
  level: SensoryLevel;
  description: string;
}> = [
  {
    level: "low",
    description: "Generally quieter with fewer known sensory triggers.",
  },
  {
    level: "medium",
    description: "Some busy or potentially stimulating sections.",
  },
  {
    level: "high",
    description: "Several known sensory triggers may occur along this route.",
  },
];

export function SensoryLoadGuide({
  compact = false,
}: SensoryLoadGuideProps) {
  return (
    <section
      className={`${styles.guide} ${
        compact ? styles.compact : ""
      }`}
      aria-label="Sensory load guide"
    >
      <p className={styles.eyebrow}>Sensory load guide</p>

      <h2 className={styles.title}>Know before you walk</h2>

      <div className={styles.list}>
        {GUIDE_ITEMS.map(({ level, description }) => {
          const presentation = SENSORY_LEVEL_PRESENTATION[level];

          return (
            <div className={styles.item} key={level}>
              <span
                className={`${styles.glyph} ${styles[level]}`}
                aria-hidden="true"
              >
                {presentation.glyph}
              </span>

              <strong className={styles.label}>
                {presentation.label}
              </strong>

              <span className={styles.description}>
                {description}
              </span>
            </div>
          );
        })}
      </div>

      <p className={styles.note}>
        Levels use words and shapes as well as colour.
      </p>
    </section>
  );
}