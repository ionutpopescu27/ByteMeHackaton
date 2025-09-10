import React, { createContext, useContext, useMemo, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState("normal"); // "admin" | "normal"

  useEffect(() => {
    const t = localStorage.getItem("auth_token");
    const r = localStorage.getItem("auth_role");
    if (t) setToken(t);
    if (r) setRole(r);
  }, []);

  const value = useMemo(
    () => ({
      token,
      role,
      isAuthenticated: !!token,
      login: (newToken, newRole = "normal") => {
        localStorage.setItem("auth_token", newToken);
        localStorage.setItem("auth_role", newRole);
        setToken(newToken);
        setRole(newRole);
      },
      logout: () => {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_role");
        setToken(null);
        setRole("normal");
      },
      setRole: (r) => {
        localStorage.setItem("auth_role", r);
        setRole(r);
      },
    }),
    [token, role]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
