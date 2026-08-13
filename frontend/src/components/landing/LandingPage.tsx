import { LogoMark } from "../brand/LogoMark";
import styles from "./LandingPage.module.css";

interface LandingPageProps {
  onEnter: () => void;
}

export function LandingPage({ onEnter }: LandingPageProps) {
  return (
    <main className={styles.page}>
      <div className={styles.backgroundPattern} aria-hidden="true" />
      <div className={styles.cityBackdrop} aria-hidden="true" />

      <section
        className={styles.content}
        aria-labelledby="landing-title"
      >
        <h1 id="landing-title" className={styles.title}>
          Synora
        </h1>

        <p className={styles.subtitle}>
          Calm walking routes and quiet spaces around Melbourne&apos;s CBD
        </p>

        <button
          type="button"
          className={styles.logoButton}
          onClick={onEnter}
          aria-label="Enter Synora"
        >
          <LogoMark className={styles.logo} />
        </button>

        <p className={styles.hint}>
          Click the logo to begin
        </p>
      </section>
    </main>
  );
}