interface LogoMarkProps {
  className?: string;
}

export function LogoMark({ className }: LogoMarkProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 40 40"
      aria-hidden="true"
      focusable="false"
    >
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
  );
}