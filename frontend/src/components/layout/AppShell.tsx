import { useState, type ReactNode } from "react";
import { LogoMark } from "../brand/LogoMark";
import { InformationPanel } from "./InformationPanel";
import styles from "./AppShell.module.css";

interface AppShellProps {
  map: ReactNode;
  mapOverlay?: ReactNode;
  sidePanel: ReactNode;
  onBackToLanding: () => void;
}

interface BrandMarkProps {
  onClick: () => void;
}

function BrandMark({ onClick }: BrandMarkProps) {
  return (
    <button
      type="button"
      className={styles.brandMark}
      onClick={onClick}
      aria-label="Return to Synora landing page"
      title="Return to landing page"
    >
      <LogoMark />
    </button>
  );
}

export function AppShell({
  map,
  mapOverlay,
  sidePanel,
  onBackToLanding,
}: AppShellProps) {
  const [panelOpen, setPanelOpen] = useState(false);
  const [infoOpen, setInfoOpen] = useState(false);

  function handleTogglePlanner() {
    setInfoOpen(false);
    setPanelOpen((current) => !current);
  }

  function handleOpenInformation() {
    setPanelOpen(false);
    setInfoOpen(true);
  }

  return (
    <div className={styles.shell}>
      <a
        href="#side-panel"
        className="skip-link"
        onClick={() => {
          setInfoOpen(false);
          setPanelOpen(true);
        }}
      >
        Skip to controls
      </a>

      <div className={styles.body}>
        <div className={styles.mapArea}>
          {map}

          {mapOverlay && (
            <div className={styles.mapOverlay}>
              {mapOverlay}
            </div>
          )}
        </div>
      </div>

      <div className={styles.floatingLayer}>
        <header className={styles.header}>
          <BrandMark onClick={onBackToLanding} />

          <div className={styles.brandText}>
            <h1 className={styles.headerTitle}>
              Synora
            </h1>

            <p className={styles.headerSubtitle}>
              Calm walking routes and quiet spaces around
              Melbourne&apos;s CBD
            </p>
          </div>
        </header>

        <div className={styles.panelArea}>
          <button
            type="button"
            className={`${styles.menuButton} ${
              panelOpen
                ? styles.menuButtonOpen
                : styles.menuButtonClosed
            }`}
            aria-label={
              panelOpen
                ? "Close route planner"
                : "Open route planner"
            }
            aria-expanded={panelOpen}
            aria-controls="side-panel"
            onClick={handleTogglePlanner}
          >
            {panelOpen ? "×" : "☰"}
          </button>

          {!panelOpen && !infoOpen && (
            <button
              type="button"
              className={styles.infoButton}
              aria-label="About this planner"
              aria-expanded={false}
              aria-controls="information-panel"
              title="About this planner"
              onClick={handleOpenInformation}
            >
              <span aria-hidden="true">i</span>
            </button>
          )}

          <div
            className={`${styles.sidePanel} ${
              panelOpen
                ? styles.sidePanelOpen
                : styles.sidePanelClosed
            }`}
            id="side-panel"
            tabIndex={-1}
          >
            {sidePanel}
          </div>

          {panelOpen && (
            <div
              className={styles.sidePanelTopFade}
              aria-hidden="true"
            />
          )}

          {infoOpen && (
            <div
              className={styles.informationOverlay}
              id="information-panel"
            >
              <InformationPanel
                onClose={() => setInfoOpen(false)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}