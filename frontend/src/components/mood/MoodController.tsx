import { useMoodStore, MoodLevel } from "../../state/mood";

const moods: MoodLevel[] = ["neutral", "calm", "focused", "energized"];

export default function MoodController() {
  const mood = useMoodStore((s) => s.mood);
  const setMood = useMoodStore((s) => s.setMood);

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-neutral-500">
        Workspace tone
      </p>

      <div className="flex gap-2">
        {moods.map((m) => (
          <button
            key={m}
            onClick={() => setMood(m)}
            className={`rounded-lg border px-3 py-1.5 text-xs transition
              ${
                mood === m
                  ? "border-neutral-900 text-neutral-900"
                  : "border-neutral-200 text-neutral-500 hover:border-neutral-400"
              }
            `}
          >
            {m}
          </button>
        ))}
      </div>
    </div>
  );
}
