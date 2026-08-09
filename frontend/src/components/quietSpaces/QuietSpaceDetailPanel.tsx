import type { QuietSpace } from "../../api/types";
import { Button } from "../common/Button";
import styles from "./QuietSpaceResultsPanel.module.css";

interface QuietSpaceDetailPanelProps {
  space: QuietSpace;
  onBack: () => void;
}

export function QuietSpaceDetailPanel({ space, onBack }: QuietSpaceDetailPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="quiet-space-detail-heading">
      <h2 id="quiet-space-detail-heading" className={styles.title}>
        {space.name}
      </h2>
      <p className={styles.itemMeta}>
        {space.type} · {space.distance_m} m away
      </p>
      <Button type="button" variant="secondary" onClick={onBack}>
        Back to results
      </Button>
    </section>
  );
}
