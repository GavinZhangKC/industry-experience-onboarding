import { SensoryLoadGuide } from "../routes/SensoryLoadGuide";
import styles from "./InformationPanel.module.css";

interface InformationPanelProps {
  onClose: () => void;
}

export function InformationPanel({
  onClose,
}: InformationPanelProps) {
  return (
    <aside
      className={styles.panel}
      aria-labelledby="information-panel-title"
    >
      <div className={styles.scrollArea}>
        <button
          type="button"
          className={styles.closeButton}
          aria-label="Close information"
          onClick={onClose}
        >
          ×
        </button>

        <div className={styles.content}>
          <p className={styles.eyebrow}>
            Sensory-aware route planning
          </p>

          <h2
            className={styles.title}
            id="information-panel-title"
          >
            Choose a route that works for you.
          </h2>

          <p className={styles.introduction}>
            This planner compares alternative walking routes
            through Melbourne CBD and helps users avoid sensory
            triggers such as crowds, noise, construction zones
            and major events.
          </p>

          <ul className={styles.features}>
            <li>
              <span aria-hidden="true">◇</span>
              Compare alternative routes
            </li>

            <li>
              <span aria-hidden="true">✓</span>
              Set sensory preferences
            </li>

            <li>
              <span aria-hidden="true">○</span>
              Find nearby quiet spaces
            </li>
          </ul>

          <SensoryLoadGuide compact />

          <section className={styles.explanation}>
            <h3>How sensory scores are calculated</h3>

            <p>
              Each route receives a sensory load score from 0
              to 100 based on available environmental data and
              known busy areas. Lower scores suggest a
              potentially calmer route.
            </p>

            <p className={styles.disclaimer}>
              Conditions may change. Scores support route
              comparison but do not guarantee a quiet or
              hazard-free journey.
            </p>
          </section>
        </div>
      </div>
    </aside>
  );
}