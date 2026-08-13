import type { PredictiveAlert } from "../../api/types";
import styles from "./PredictiveAlerts.module.css";

interface PredictiveAlertsProps {
  alerts: PredictiveAlert[];
}

// Surfaced passively (fetched once on load, not behind a button) since the
// DoD language is "users receive... alerts", not "users can look up
// alerts". Renders nothing at all when the list is empty — including on
// mock/local data, where trending_areas is always [] — rather than showing
// an empty state for a feature that isn't the main flow.
export function PredictiveAlerts({ alerts }: PredictiveAlertsProps) {
  if (alerts.length === 0) return null;

  return (
    <div className={styles.wrapper} role="status" aria-label="Predictive crowd alerts">
      {alerts.slice(0, 3).map((alert) => (
        <p key={alert.id} className={styles.alert}>
          <span className={styles.icon} aria-hidden="true">
            ⚠
          </span>
          {alert.message}
        </p>
      ))}
    </div>
  );
}
