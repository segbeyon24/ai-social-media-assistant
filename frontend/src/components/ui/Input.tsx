import { InputHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={clsx(
          "w-full rounded-md border px-3 py-2 text-sm outline-none transition",
          "focus:ring-2 focus:ring-offset-1",
          {
            "border-neutral-300 focus:ring-black": !error,
            "border-red-500 focus:ring-red-500": error,
          },
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";
