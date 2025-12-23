import { ReactNode } from "react";
import TopBar from "@/components/layout/TopBar";

interface WorkspaceLayoutProps {
  children: ReactNode;
}

const WorkspaceLayout = ({ children }: WorkspaceLayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col bg-neutral-950 text-neutral-100">
      <TopBar />

      <main className="flex-1 flex justify-center px-4 py-6">
        <div className="w-full max-w-3xl">
          {children}
        </div>
      </main>
    </div>
  );
};

export default WorkspaceLayout;
