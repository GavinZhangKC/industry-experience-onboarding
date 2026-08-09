import { forwardRef } from "react";
import type { ButtonHTMLAttributes } from "react";
import styles from "./Button.module.css";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", className, ...rest },
  ref,
) {
  const variantClass = variant === "primary" ? styles.primary : styles.secondary;
  return (
    <button ref={ref} className={[styles.button, variantClass, className].filter(Boolean).join(" ")} {...rest} />
  );
});
