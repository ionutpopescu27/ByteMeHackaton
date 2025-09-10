import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Usage:
 *   <Route element={<PrivateRoute />}> ...</Route>               // any authenticated user
 *   <Route element={<PrivateRoute allowed={["normal"]} />}> ...  // only normal users
 *   <Route element={<PrivateRoute allowed={["admin"]} />}> ...   // only admins
 */
export default function PrivateRoute({ allowed }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (allowed && !allowed.includes(role)) {
    // Not permitted for this role
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
