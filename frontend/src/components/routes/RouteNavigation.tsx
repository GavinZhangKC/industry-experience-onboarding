import type { RouteOption } from "../../api/types";
import styles from "./RouteNavigation.module.css";

interface RouteNavigationProps {
  route: RouteOption;
  currentStepIndex: number;
  onNextStep: () => void;
  onPreviousStep: () => void;
  onExit: () => void;
}

function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60);
  if (minutes < 1) return "under 1 min";
  return `${minutes} min`;
}

function formatDistance(metres: number): string {
  if (metres >= 1000) {
    return `${(metres / 1000).toFixed(1)} km`;
  }
  return `${Math.round(metres)} m`;
}

// A step-through instruction list, not live GPS-tracked navigation — there's
// no continuous location tracking or automatic step-advancement here, only
// manual Next/Back. Framed honestly as that in the UI copy below, since
// overclaiming "turn-by-turn navigation" for something that doesn't track
// your actual position would be misleading.
export function RouteNavigation({
  route,
  currentStepIndex,
  onNextStep,
  onPreviousStep,
  onExit,
}: RouteNavigationProps) {
  const steps = route.steps;
  const hasSteps = steps.length > 0;
  const step = hasSteps ? steps[currentStepIndex] : null;
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === steps.length - 1;

  const remainingDistance = hasSteps
    ? steps.slice(currentStepIndex).reduce((sum, s) => sum + s.distance_m, 0)
    : route.distance_m;
  const remainingDuration = hasSteps
    ? steps.slice(currentStepIndex).reduce((sum, s) => sum + s.duration_s, 0)
    : route.duration_s;

  return (
    <aside className={styles.card} aria-label={`Navigating ${route.label}`}>
      <div className={styles.header}>
        <span className={styles.title}>Navigating {route.label}</span>
        <button type="button" className={styles.exitButton} onClick={onExit}>
          Exit
        </button>
      </div>

      {!hasSteps && (
        <p className={styles.noSteps}>
          Step-by-step directions aren't available for this route — here's the overall distance and time instead.
        </p>
      )}

      {hasSteps && step && (
        <>
          <p className={styles.stepCount}>
            Step {currentStepIndex + 1} of {steps.length}
          </p>
          <p className={styles.instruction}>{step.instruction}</p>
          <p className={styles.stepMeta}>
            {formatDistance(step.distance_m)} · {formatDuration(step.duration_s)}
          </p>
        </>
      )}

      <p className={styles.remaining}>
        {formatDistance(remainingDistance)} · {formatDuration(remainingDuration)} remaining
      </p>

      {hasSteps && (
        <div className={styles.controls}>
          <button
            type="button"
            className={styles.navButton}
            onClick={onPreviousStep}
            disabled={isFirstStep}
          >
            Back
          </button>
          <button
            type="button"
            className={styles.navButton}
            onClick={onNextStep}
            disabled={isLastStep}
          >
            {isLastStep ? "Arrived" : "Next"}
          </button>
        </div>
      )}
    </aside>
  );
}
