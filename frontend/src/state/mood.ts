import { create } from "zustand";

export type MoodLevel = "neutral" | "calm" | "focused" | "energized";

interface MoodState {
  mood: MoodLevel;
  setMood: (mood: MoodLevel) => void;
}

export const useMoodStore = create<MoodState>((set) => ({
  mood: "neutral",
  setMood: (mood) => set({ mood }),
}));
