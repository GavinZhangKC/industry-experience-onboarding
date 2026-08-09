import type { ReactNode } from "react";
import styles from "./AppShell.module.css";

interface AppShellProps {
  map: ReactNode;
  sidePanel: ReactNode;
  quietSpaceBar: ReactNode;
}

export function AppShell({ map, sidePanel, quietSpaceBar }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <a href="#side-panel" className="skip-link">
        Skip to controls
      </a>
      <header className={styles.header}>
        <h1 className={styles.headerTitle}>Sensory-Aware Route Planner</h1>
        <p className={styles.headerSubtitle}>Calm walking routes and quiet spaces around Melbourne's CBD</p>
      </header>
      <div className={styles.body}>
        <div className={styles.mapArea}>{map}</div>
        <div className={styles.sidePanel} id="side-panel" tabIndex={-1}>
          {sidePanel}
        </div>
      </div>
      {quietSpaceBar}
    </div>
  );
}
