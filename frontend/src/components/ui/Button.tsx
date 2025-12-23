import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      loading = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(
          "inline-flex items-center justify-center rounded-md font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2",
          {
            "bg-black text-white hover:bg-neutral-800 focus:ring-black":
              variant === "primary",
            "bg-neutral-100 text-black hover:bg-neutral-200 focus:ring-neutral-400":
              variant === "secondary",
            "bg-transparent text-black hover:bg-neutral-100":
              variant === "ghost",
            "bg-red-600 text-white hover:bg-red-700 focus:ring-red-600":
              variant === "danger",
            "px-3 py-1.5 text-sm": size === "sm",
            "px-4 py-2 text-sm": size === "md",
            "px-5 py-3 text-base": size === "lg",
            "opacity-60 cursor-not-allowed": disabled || loading,
          },
          className
        )}
        {...props}
      >
        {loading ? "…" : children}
      </button>
    );
  }
);

Button.displayName = "Button";
