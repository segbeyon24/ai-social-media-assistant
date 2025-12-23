import { TextareaHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={clsx(
          "w-full resize-none rounded-md border px-3 py-2 text-sm outline-none transition",
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

Textarea.displayName = "Textarea";
