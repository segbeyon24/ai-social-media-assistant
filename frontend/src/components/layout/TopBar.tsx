import { useState } from "react";
import { Clock, LayoutGrid } from "lucide-react";
import { IconButton } from "../ui/IconButton";
import { supabase } from "../../lib/supabase";
import { useAuthStore } from "../../state/auth";

type TopTab = "history" | "feeds";

const TopBar = () => {
  const [activeTab, setActiveTab] = useState<TopTab>("feeds");
  const logout = async () => {
    await supabase.auth.signOut();
    useAuthStore.getState().clear();
  };
  return (
    <header className="h-14 flex items-center justify-between px-4 border-b border-[var(--border-color)] bg-[var(--bg-main)]">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium tracking-wide text-[var(--text-muted)]">
          LeanSocial
        </span>
      </div>

      <nav className="flex items-center gap-2">
        <IconButton
          icon={Clock}
          ariaLabel="History"
          active={activeTab === "history"}
          onClick={() => setActiveTab("history")}
        />

        <IconButton
          icon={LayoutGrid}
          ariaLabel="Feeds"
          active={activeTab === "feeds"}
          onClick={() => setActiveTab("feeds")}
        />

        <IconButton
          icon={LayoutGrid}
          ariaLabel="logout"
          onClick={logout}
        />
      </nav>
    </header>
  );
};

export default TopBar;
