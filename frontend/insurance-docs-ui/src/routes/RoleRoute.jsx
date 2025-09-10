import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RoleRoute({ allowed }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!allowed.includes(role)) {
    // If blocked, send them home (or wherever you prefer)
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
