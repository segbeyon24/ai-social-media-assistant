import { Routes, Route } from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";
import PublicRoute from "./PublicRoute";

import Home from "../pages/Home/Home";
import Login from "../pages/Auth/Login";
import Signup from "../pages/Auth/Signup";
import Workspace from "../pages/Workspace/Workspace";
import AuthCallback from "../pages/Auth/AuthCallback";
import NotFound from "../pages/NotFound";

export function AppRouter() {
  return (
    <Routes>
      {/* OAuth callback — MUST be public and isolated */}
      <Route path="/auth/callback" element={<AuthCallback />} />

      {/* Public */}
      <Route path="/" element={<Home />} />

      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      <Route
        path="/signup"
        element={
          <PublicRoute>
            <Signup />
          </PublicRoute>
        }
      />

      {/* Protected */}
      <Route
        path="/me"
        element={
          <ProtectedRoute>
            <Workspace />
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
