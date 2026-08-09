interface LoadingStateProps {
  label: string;
}

export function LoadingState({ label }: LoadingStateProps) {
  return (
    <p role="status" aria-live="polite" style={{ color: "var(--color-text-muted)" }}>
      {label}
    </p>
  );
}
