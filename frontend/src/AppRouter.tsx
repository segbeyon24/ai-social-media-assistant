import { Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import { useAuthStore } from "./state/auth";

export function AppRouter() {
  const session = useAuthStore((s) => s.session);

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={!session ? <Login /> : <Navigate to="/me" replace />} />
      <Route path="/me" element={session ? <Dashboard /> : <Navigate to="/login" replace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
