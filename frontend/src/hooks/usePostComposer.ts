import { useCallback } from "react";
import { usePostStore } from "../state/post";
import type { PostDraft } from "../types/post";

export function usePostComposer() {
  const { draft, isSubmitting, setDraft, setSubmitting, reset } =
    usePostStore();

  const submit = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setSubmitting(true);

    const next: PostDraft = {
      content,
      createdAt: Date.now(),
    };

    setDraft(next);
    setSubmitting(false);
  }, [setDraft, setSubmitting]);

  return {
    draft,
    isSubmitting,
    submit,
    reset,
  };
}
