import { useState, type ReactNode } from "react";
import styles from "./AppShell.module.css";

interface AppShellProps {
  map: ReactNode;
  sidePanel: ReactNode;
}

function BrandMark() {
  return (
    <div className={styles.brandMark} aria-hidden="true">
      <svg viewBox="0 0 40 40">
        <path
          d="M11 29C11 22 16 23 16 17C16 13.5 18.5 11 22 11C26 11 29 14 29 18C29 24 23 25 23 30"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
        />

        <circle cx="11" cy="29" r="3" fill="currentColor" />
        <circle cx="29" cy="18" r="3" fill="currentColor" />
      </svg>
    </div>
  );
}

export function AppShell({ map, sidePanel }: AppShellProps) {
  const [panelOpen, setPanelOpen] = useState(false);

  return (
    <div className={styles.shell}>
      <a
        href="#side-panel"
        className="skip-link"
        onClick={() => setPanelOpen(true)}
      >
        Skip to controls
      </a>

      <div className={styles.body}>
        <div className={styles.mapArea}>{map}</div>
      </div>

      <div className={styles.floatingLayer}>
        <header className={styles.header}>
          <BrandMark />

          <div className={styles.brandText}>
            <h1 className={styles.headerTitle}>
              Sensory-Aware Route Planner
            </h1>

            <p className={styles.headerSubtitle}>
              Calm walking routes and quiet spaces around Melbourne&apos;s CBD
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
            onClick={() => setPanelOpen((current) => !current)}
          >
            {panelOpen ? "×" : "☰"}
          </button>

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
        </div>
      </div>
    </div>
  );
}