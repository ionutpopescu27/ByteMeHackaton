import React, { createContext, useContext, useMemo, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const t = localStorage.getItem("auth_token");
    if (t) setToken(t);
  }, []);

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: !!token,
      login: (newToken) => {
        localStorage.setItem("auth_token", newToken);
        setToken(newToken);
      },
      logout: () => {
        localStorage.removeItem("auth_token");
        setToken(null);
      },
    }),
    [token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
