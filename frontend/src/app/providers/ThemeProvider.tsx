import { ReactNode, useEffect } from "react";
import { useMoodStore } from "../../state/mood";

interface Props {
  children: ReactNode;
}

export function ThemeProvider({ children }: Props) {
  const mood = useMoodStore((s) => s.mood);

  useEffect(() => {
    const root = document.documentElement;

    // Mood affects workspace globally (session-wide)
    root.setAttribute("data-mood", mood);
  }, [mood]);

  return <>{children}</>;
}
