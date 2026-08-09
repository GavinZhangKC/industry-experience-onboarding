import { useEffect, useRef } from "react";
import { Button } from "../common/Button";
import styles from "./QuietSpaceResultsPanel.module.css";

interface ExpandRadiusDialogProps {
  message: string;
  nextRadiusM: number | null;
  onExpand: () => void;
  onDismiss: () => void;
}

export function ExpandRadiusDialog({ message, nextRadiusM, onExpand, onDismiss }: ExpandRadiusDialogProps) {
  const expandButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    expandButtonRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onDismiss();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onDismiss]);

  return (
    <div className={styles.dialogOverlay}>
      <div
        className={styles.dialog}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="expand-radius-heading"
        aria-describedby="expand-radius-message"
      >
        <h3 id="expand-radius-heading">No quiet spaces found</h3>
        <p id="expand-radius-message">{message}</p>
        <div className={styles.dialogActions}>
          {nextRadiusM !== null && (
            <Button type="button" ref={expandButtonRef} onClick={onExpand}>
              Search within {nextRadiusM >= 1000 ? `${nextRadiusM / 1000} km` : `${nextRadiusM} m`}
            </Button>
          )}
          <Button type="button" variant="secondary" onClick={onDismiss}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
