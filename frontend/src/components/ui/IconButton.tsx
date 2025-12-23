import { ButtonHTMLAttributes } from "react";
import clsx from "clsx";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
}

export function IconButton({
  className,
  label,
  children,
  ...props
}: IconButtonProps) {
  return (
    <button
      aria-label={label}
      className={clsx(
        "inline-flex items-center justify-center rounded-md p-2 transition hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-neutral-400",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
