import { useId } from "react";
import type { Coordinate } from "../../api/types";
import { MELBOURNE_LANDMARKS } from "../../constants/landmarks";
import styles from "./LocationSelect.module.css";

interface LocationSelectProps {
  label: string;
  kind: "origin" | "destination";
  value: Coordinate | null;
  selectedLandmarkId: string | null;
  onSelectLandmark: (landmarkId: string) => void;
  isPicking: boolean;
  onTogglePicking: () => void;
}

function MapPinIcon() {
  return (
    <svg
      width="25"
      height="25"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
      <circle cx="12" cy="10" r="2.5" />
      <path d="M6 21h12" />
    </svg>
  );
}

export function LocationSelect({
  label,
  kind,
  value,
  selectedLandmarkId,
  onSelectLandmark,
  isPicking,
  onTogglePicking,
}: LocationSelectProps) {
  const selectId = useId();

  const isCustomPoint =
    value !== null && selectedLandmarkId === null;

  return (
    <div className={styles.fieldRow}>
      <span
        className={
          kind === "origin"
            ? styles.originMarker
            : styles.destinationMarker
        }
        aria-hidden="true"
      />

      <div className={styles.field}>
        <label className="visually-hidden" htmlFor={selectId}>
          {label}
        </label>

        <div className={styles.inputShell}>
          <select
            id={selectId}
            className={styles.select}
            value={
              isCustomPoint
                ? "__custom__"
                : selectedLandmarkId ?? ""
            }
            onChange={(event) =>
              onSelectLandmark(event.target.value)
            }
          >
            <option value="">{label}</option>

            {isCustomPoint && (
              <option value="__custom__" disabled>
                Custom map point
              </option>
            )}

            {MELBOURNE_LANDMARKS.map((landmark) => (
              <option key={landmark.id} value={landmark.id}>
                {landmark.name}
              </option>
            ))}
          </select>

          <button
            type="button"
            className={`${styles.pickButton} ${
              isPicking ? styles.pickButtonActive : ""
            }`}
            aria-label={`Pick ${label.toLowerCase()} on map`}
            aria-pressed={isPicking}
            title={
              isPicking
                ? "Cancel map selection"
                : "Pick on map"
            }
            onClick={onTogglePicking}
          >
            <MapPinIcon />
          </button>
        </div>

        {isPicking && (
          <p className={styles.hint} role="status">
            Click anywhere on the map to set the{" "}
            {label.toLowerCase()} location.
          </p>
        )}

        {isCustomPoint && !isPicking && (
          <p className={styles.customPoint}>
            Selected point: {value.lat.toFixed(4)},{" "}
            {value.lng.toFixed(4)}
          </p>
        )}
      </div>
    </div>
  );
}