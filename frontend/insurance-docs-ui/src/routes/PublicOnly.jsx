// src/routes/PublicOnly.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Wrap public pages (login/register/forgot).
 * If user is already authenticated, bounce them away.
 */
export default function PublicOnly({ children }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (isAuthenticated) {
    // Send authenticated users to their default landing
    return <Navigate to={role === "normal" ? "/transcripts" : "/"} replace state={{ from: location }} />;
  }
  return children;
}
