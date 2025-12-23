import { useState } from "react";
import { Clock, LayoutGrid } from "lucide-react";
import IconButton from "../ui/IconButton";

type TopTab = "history" | "feeds";

const TopBar = () => {
  const [activeTab, setActiveTab] = useState<TopTab>("feeds");

  return (
    <header className="h-14 flex items-center justify-between px-4 border-b border-neutral-800 bg-neutral-900">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium tracking-wide text-neutral-300">
          Workspace
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
      </nav>
    </header>
  );
};

export default TopBar;
