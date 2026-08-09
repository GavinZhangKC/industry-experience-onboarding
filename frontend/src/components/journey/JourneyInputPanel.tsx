import type { ApiError, Coordinate } from "../../api/types";
import { Button } from "../common/Button";
import { ErrorBanner } from "../common/ErrorBanner";
import { LoadingState } from "../common/LoadingState";
import { LocationSelect } from "./LocationSelect";
import styles from "./JourneyInputPanel.module.css";
import { SensoryPreferences } from "./SensoryPreferences";

export type PickingField = "origin" | "destination" | null;

interface JourneyInputPanelProps {
  origin: Coordinate | null;
  destination: Coordinate | null;
  originLandmarkId: string | null;
  destinationLandmarkId: string | null;
  pickingField: PickingField;
  onSelectLandmark: (field: "origin" | "destination", landmarkId: string) => void;
  onTogglePicking: (field: "origin" | "destination") => void;
  onClearField: (field: "origin" | "destination") => void;
  onClearAll: () => void;
  onSearch: () => void;
  loading: boolean;
  error: ApiError | null;
}

export function JourneyInputPanel({
  origin,
  destination,
  originLandmarkId,
  destinationLandmarkId,
  pickingField,
  onSelectLandmark,
  onTogglePicking,
  onClearAll,
  onSearch,
  loading,
  error,
}: JourneyInputPanelProps) {
  const canSearch = origin !== null && destination !== null && !loading;

  return (
    <section className={styles.panel} aria-labelledby="journey-input-heading">
      <h2 id="journey-input-heading" className="visually-hidden">
        Plan a calm route
      </h2>
      <div className={styles.locationGroup}>
        <LocationSelect
          label="From"
          kind="origin"
          value={origin}
          selectedLandmarkId={originLandmarkId}
          onSelectLandmark={(id) => onSelectLandmark("origin", id)}
          isPicking={pickingField === "origin"}
          onTogglePicking={() => onTogglePicking("origin")}
        />

        <div className={styles.directionArrow} aria-hidden="true">
          ↓
        </div>

        <LocationSelect
          label="To"
          kind="destination"
          value={destination}
          selectedLandmarkId={destinationLandmarkId}
          onSelectLandmark={(id) => onSelectLandmark("destination", id)}
          isPicking={pickingField === "destination"}
          onTogglePicking={() => onTogglePicking("destination")}
        />
      </div>
      <div className={styles.actions}>
        <Button type="button" variant="secondary" onClick={onClearAll}>
          Reset
        </Button>

        <Button type="button" onClick={onSearch} disabled={!canSearch}>
          {loading ? "Finding routes…" : "Find routes"}
        </Button>
      </div>
      {loading && <LoadingState label="Looking for calm routes…" />}
      {error && <ErrorBanner message={error.message} />}

      <SensoryPreferences />
    </section>
  );
}
