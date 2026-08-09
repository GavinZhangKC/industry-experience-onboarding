import styles from "./ErrorBanner.module.css";

interface ErrorBannerProps {
  message: string;
}

// Always renders exactly the message the caller passes — callers switch on
// ApiError.code to decide what to show/do, but never parse message text.
export function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className={styles.banner} role="alert">
      <span className={styles.icon} aria-hidden="true">
        ⚠
      </span>
      <span>{message}</span>
    </div>
  );
}
