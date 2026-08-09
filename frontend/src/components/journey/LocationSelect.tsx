import { useId } from "react";
import type { Coordinate } from "../../api/types";
import { MELBOURNE_LANDMARKS } from "../../constants/landmarks";
import styles from "./LocationSelect.module.css";

interface LocationSelectProps {
  label: string;
  value: Coordinate | null;
  selectedLandmarkId: string | null;
  onSelectLandmark: (landmarkId: string) => void;
  isPicking: boolean;
  onTogglePicking: () => void;
  onClear: () => void;
}

export function LocationSelect({
  label,
  value,
  selectedLandmarkId,
  onSelectLandmark,
  isPicking,
  onTogglePicking,
  onClear,
}: LocationSelectProps) {
  const selectId = useId();
  const isCustomPoint = value !== null && selectedLandmarkId === null;

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={selectId}>
        {label}
      </label>
      <div className={styles.row}>
        <select
          id={selectId}
          className={styles.select}
          value={selectedLandmarkId ?? ""}
          onChange={(event) => onSelectLandmark(event.target.value)}
        >
          <option value="">Select a landmark…</option>
          {MELBOURNE_LANDMARKS.map((landmark) => (
            <option key={landmark.id} value={landmark.id}>
              {landmark.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          className={`${styles.pickButton} ${isPicking ? styles.pickButtonActive : ""}`}
          aria-pressed={isPicking}
          onClick={onTogglePicking}
        >
          {isPicking ? "Click the map…" : "Pick on map"}
        </button>
        {value && (
          <button type="button" className={styles.clearButton} onClick={onClear}>
            Clear {label.toLowerCase()}
          </button>
        )}
      </div>
      {isPicking && (
        <p className={styles.hint} role="status">
          Click anywhere on the map to set the {label.toLowerCase()}.
        </p>
      )}
      {isCustomPoint && (
        <p className={styles.customPoint}>
          Custom point: {value.lat.toFixed(4)}, {value.lng.toFixed(4)}
        </p>
      )}
    </div>
  );
}
