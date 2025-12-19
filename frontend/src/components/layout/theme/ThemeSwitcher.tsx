import { useTheme } from "../../state/theme";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">Theme</label>
      <select
        value={theme}
        onChange={(e) => setTheme(e.target.value)}
        className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2"
      >
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="graphite">Graphite</option>
      </select>
    </div>
  );
}
