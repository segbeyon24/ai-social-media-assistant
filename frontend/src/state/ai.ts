import { create } from "zustand";
import type { AIMessage } from "@/types/ai";

interface AIState {
  messages: AIMessage[];
  isThinking: boolean;

  addMessage: (m: AIMessage) => void;
  setThinking: (v: boolean) => void;
  reset: () => void;
}

export const useAIStore = create<AIState>((set) => ({
  messages: [],
  isThinking: false,

  addMessage: (m) =>
    set((s) => ({ messages: [...s.messages, m] })),

  setThinking: (v) => set({ isThinking: v }),

  reset: () => set({ messages: [], isThinking: false }),
}));
