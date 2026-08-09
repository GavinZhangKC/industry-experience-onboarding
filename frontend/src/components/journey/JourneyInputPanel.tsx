import type { ApiError, Coordinate } from "../../api/types";
import { Button } from "../common/Button";
import { ErrorBanner } from "../common/ErrorBanner";
import { LoadingState } from "../common/LoadingState";
import { LocationSelect } from "./LocationSelect";
import styles from "./JourneyInputPanel.module.css";

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
  onClearField,
  onClearAll,
  onSearch,
  loading,
  error,
}: JourneyInputPanelProps) {
  const canSearch = origin !== null && destination !== null && !loading;

  return (
    <section className={styles.panel} aria-labelledby="journey-input-heading">
      <h2 id="journey-input-heading" className={styles.title}>
        Plan a calm route
      </h2>
      <LocationSelect
        label="Origin"
        value={origin}
        selectedLandmarkId={originLandmarkId}
        onSelectLandmark={(id) => onSelectLandmark("origin", id)}
        isPicking={pickingField === "origin"}
        onTogglePicking={() => onTogglePicking("origin")}
        onClear={() => onClearField("origin")}
      />
      <LocationSelect
        label="Destination"
        value={destination}
        selectedLandmarkId={destinationLandmarkId}
        onSelectLandmark={(id) => onSelectLandmark("destination", id)}
        isPicking={pickingField === "destination"}
        onTogglePicking={() => onTogglePicking("destination")}
        onClear={() => onClearField("destination")}
      />
      <div className={styles.actions}>
        <Button type="button" onClick={onSearch} disabled={!canSearch}>
          {loading ? "Searching…" : "Search routes"}
        </Button>
        <Button type="button" variant="secondary" onClick={onClearAll}>
          Clear all
        </Button>
      </div>
      {loading && <LoadingState label="Looking for calm routes…" />}
      {error && <ErrorBanner message={error.message} />}
    </section>
  );
}
