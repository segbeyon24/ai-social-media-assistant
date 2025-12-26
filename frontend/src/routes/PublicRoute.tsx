import { Navigate } from "react-router-dom";
import { ReactNode } from "react";
import { useAuthStore } from "../state/auth";

interface Props {
  children: ReactNode;
}

export default function PublicRoute({ children }: Props) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-neutral-500">
        Loading…
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/me" replace />;
  }

  return <>{children}</>;
}
