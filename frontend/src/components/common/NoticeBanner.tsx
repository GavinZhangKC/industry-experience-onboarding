import styles from "./NoticeBanner.module.css";

interface NoticeBannerProps {
  message: string;
}

// For informational messages (e.g. "falling back to X"), not failures —
// visually distinct from ErrorBanner so a graceful fallback doesn't read as
// something broken.
export function NoticeBanner({ message }: NoticeBannerProps) {
  return (
    <div className={styles.banner} role="status">
      <span className={styles.icon} aria-hidden="true">
        ℹ
      </span>
      <span>{message}</span>
    </div>
  );
}
