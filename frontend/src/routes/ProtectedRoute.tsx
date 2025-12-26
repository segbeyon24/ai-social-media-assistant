import { Navigate } from "react-router-dom";
import { ReactNode } from "react";
import { useAuthStore } from "../state/auth";

interface Props {
  children: ReactNode;
}

export default function ProtectedRoute({ children }: Props) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return <div className="h-screen flex items-center justify-center text-sm text-neutral-500">
      Loading…
    </div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
