import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../modules/auth/hooks/useAuth";

export function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="page-shell">Loading session...</div>;
  }

  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
