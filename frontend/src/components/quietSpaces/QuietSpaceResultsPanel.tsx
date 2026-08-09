import { useEffect, useState } from "react";
import type { ApiError, QuietSpace, QuietSpaceResponse } from "../../api/types";
import { Button } from "../common/Button";
import { ErrorBanner } from "../common/ErrorBanner";
import { LoadingState } from "../common/LoadingState";
import { NoticeBanner } from "../common/NoticeBanner";
import { ExpandRadiusDialog } from "./ExpandRadiusDialog";
import { QuietSpaceDetailPanel } from "./QuietSpaceDetailPanel";
import styles from "./QuietSpaceResultsPanel.module.css";

interface QuietSpaceResultsPanelProps {
  data: QuietSpaceResponse | null;
  loading: boolean;
  error: ApiError | null;
  locationNote: string | null;
  selectedSpaceId: string | null;
  onSelectSpace: (space: QuietSpace) => void;
  onBackFromDetail: () => void;
  onClose: () => void;
  canExpand: boolean;
  nextRadiusM: number | null;
  onExpandRadius: () => void;
}

export function QuietSpaceResultsPanel({
  data,
  loading,
  error,
  locationNote,
  selectedSpaceId,
  onSelectSpace,
  onBackFromDetail,
  onClose,
  canExpand,
  nextRadiusM,
  onExpandRadius,
}: QuietSpaceResultsPanelProps) {
  const isEmpty = data !== null && data.quiet_spaces.length === 0 && !!data.message;
  const [dialogDismissed, setDialogDismissed] = useState(false);

  useEffect(() => {
    setDialogDismissed(false);
  }, [data]);

  const selectedSpace = data?.quiet_spaces.find((space) => space.id === selectedSpaceId) ?? null;

  if (selectedSpace) {
    return <QuietSpaceDetailPanel space={selectedSpace} onBack={onBackFromDetail} />;
  }

  return (
    <section className={styles.panel} aria-labelledby="quiet-space-results-heading">
      <div className={styles.headerRow}>
        <h2 id="quiet-space-results-heading" className={styles.title}>
          Quiet spaces nearby
        </h2>
        <Button type="button" variant="secondary" onClick={onClose}>
          Close
        </Button>
      </div>
      {locationNote && <NoticeBanner message={locationNote} />}
      {loading && <LoadingState label="Looking for quiet spaces…" />}
      {error && <ErrorBanner message={error.message} />}
      {data && data.quiet_spaces.length > 0 && (
        <ul className={styles.list}>
          {data.quiet_spaces.map((space) => (
            <li key={space.id}>
              <button
                type="button"
                className={styles.item}
                aria-pressed={space.id === selectedSpaceId}
                onClick={() => onSelectSpace(space)}
              >
                <div className={styles.itemName}>{space.name}</div>
                <div className={styles.itemMeta}>
                  {space.type} · {space.distance_m} m away
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
      {isEmpty && !dialogDismissed && (
        <ExpandRadiusDialog
          message={data!.message!}
          nextRadiusM={canExpand ? nextRadiusM : null}
          onExpand={onExpandRadius}
          onDismiss={() => setDialogDismissed(true)}
        />
      )}
      {isEmpty && dialogDismissed && <p className={styles.itemMeta}>{data!.message}</p>}
    </section>
  );
}
