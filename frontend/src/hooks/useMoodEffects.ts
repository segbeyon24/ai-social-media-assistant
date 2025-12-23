import { useEffect } from "react";
import { useMoodStore } from "../state/mood";

const moodMap: Record<string, Record<string, string>> = {
  neutral: {
    "--bg": "#ffffff",
    "--fg": "#0a0a0a",
    "--accent": "#e5e5e5",
  },
  calm: {
    "--bg": "#f9fafb",
    "--fg": "#0f172a",
    "--accent": "#cbd5e1",
  },
  focused: {
    "--bg": "#ffffff",
    "--fg": "#020617",
    "--accent": "#94a3b8",
  },
  energized: {
    "--bg": "#ffffff",
    "--fg": "#020617",
    "--accent": "#a5b4fc",
  },
};

export function useMoodEffects() {
  const mood = useMoodStore((s) => s.mood);

  useEffect(() => {
    const root = document.documentElement;
    const vars = moodMap[mood];

    Object.entries(vars).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  }, [mood]);
}
