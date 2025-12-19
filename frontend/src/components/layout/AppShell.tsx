import { ReactNode } from "react";
import { Sidebar } from "./sidebar/Sidebar";
import { useTheme } from "../../state/theme";

export default function AppShell({ children }: { children: ReactNode }) {
  const { theme } = useTheme();

  return (
    <div className={`min-h-screen w-full bg-[var(--bg)] text-[var(--fg)] ${theme}`}> 
      <div className="flex">
        <Sidebar />
        <main className="flex-1 px-8 py-6 transition-colors">
          {children}
        </main>
      </div>
    </div>
  );
}
