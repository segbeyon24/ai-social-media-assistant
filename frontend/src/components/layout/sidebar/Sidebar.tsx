import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Home, LayoutDashboard, Settings, ChevronLeft } from "lucide-react";

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`h-screen sticky top-0 bg-[var(--sidebar)] border-r border-[var(--border)] transition-all duration-300 ${collapsed ? "w-20" : "w-64"}`}
    >
      <div className="flex items-center justify-between px-4 py-4">
        {!collapsed && <span className="text-lg font-semibold">LeanSocial</span>}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="rounded-lg p-1 hover:bg-[var(--hover)]"
        >
          <ChevronLeft className={`transition-transform ${collapsed ? "rotate-180" : ""}`} />
        </button>
      </div>

      <nav className="mt-6 space-y-1 px-2">
        <NavLink to="/" className="nav-link">
          <Home /> {!collapsed && "Home"}
        </NavLink>
        <NavLink to="/me" className="nav-link">
          <LayoutDashboard /> {!collapsed && "Dashboard"}
        </NavLink>
        <NavLink to="/settings" className="nav-link">
          <Settings /> {!collapsed && "Settings"}
        </NavLink>
      </nav>
    </aside>
  );
}
