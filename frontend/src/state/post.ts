import { create } from "zustand";
import type { PostDraft } from "../types/post";

interface PostState {
  draft: PostDraft | null;
  isSubmitting: boolean;

  setDraft: (draft: PostDraft | null) => void;
  setSubmitting: (v: boolean) => void;
  reset: () => void;
}

export const usePostStore = create<PostState>((set) => ({
  draft: null,
  isSubmitting: false,

  setDraft: (draft) => set({ draft }),
  setSubmitting: (v) => set({ isSubmitting: v }),
  reset: () => set({ draft: null, isSubmitting: false }),
}));
