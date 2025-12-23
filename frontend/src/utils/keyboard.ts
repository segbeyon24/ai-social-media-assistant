import { KeyboardEvent } from "react";

interface KeyboardSubmitOptions {
  onSubmit: () => void;
  allowEmpty?: boolean;
  value?: string;
}

export function handleChatSubmit(
  e: KeyboardEvent,
  { onSubmit, allowEmpty = false, value }: KeyboardSubmitOptions
) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();

    if (!allowEmpty && !value?.trim()) return;
    onSubmit();
  }
}

/**
 * PostComposer-specific shortcut
 * Enter = submit
 * Shift+Enter = newline
 */
export function handleComposerKey(
  e: KeyboardEvent,
  onSubmit: () => void
) {
  handleChatSubmit(e, {
    onSubmit,
  });
}
