import { useEffect, useRef } from "react";
import { Button } from "../common/Button";
import styles from "./QuietSpaceResultsPanel.module.css";

interface ExpandRadiusDialogProps {
  message: string;
  nextRadiusM: number | null;
  onExpand: () => void;
  onDismiss: () => void;
}

export function ExpandRadiusDialog({
  message,
  nextRadiusM,
  onExpand,
  onDismiss,
}: ExpandRadiusDialogProps) {
  const expandButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    expandButtonRef.current?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onDismiss();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onDismiss]);

  const formattedRadius =
    nextRadiusM !== null
      ? nextRadiusM >= 1000
        ? `${nextRadiusM / 1000} km`
        : `${nextRadiusM} m`
      : null;

  return (
    <div className={styles.dialogOverlay}>
      <div
        className={styles.dialog}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="expand-radius-heading"
        aria-describedby="expand-radius-message"
      >
        <h3 id="expand-radius-heading">
          No quiet spaces found
        </h3>

        <p id="expand-radius-message">
          {message}
        </p>

        <div className={styles.dialogActions}>
          {nextRadiusM !== null && (
            <Button
              type="button"
              ref={expandButtonRef}
              className={styles.expandButton}
              onClick={onExpand}
            >
              Search within {formattedRadius}
            </Button>
          )}

          <Button
            type="button"
            variant="secondary"
            className={styles.closeDialogButton}
            onClick={onDismiss}
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}