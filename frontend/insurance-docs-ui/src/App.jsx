import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import PrivateRoute from "./routes/PrivateRoute.jsx";
import RoleRoute from "./routes/RoleRoute.jsx";
import PublicOnly from "./routes/PublicOnly.jsx";

// Layout
import Sidebar from "./components/Sidebar";
import Header from "./components/Header"; // remove if not used

// Pages
import Home from "./pages/Home.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import MyDocuments from "./pages/MyDocuments.jsx";
import RecentlyDeleted from "./pages/RecentlyDeleted.jsx";
import Transcripts from "./pages/Transcripts.jsx";
import Forms from "./pages/Forms.jsx"; // <-- your new forms page

// Auth screens (.js)
import Login from "./app/(auth)/login.js";
import Register from "./app/register.js";
import Forgot from "./app/forgot.js";

function AppShell() {
  const location = useLocation();
  const isAuthRoute =
    location.pathname.startsWith("/login") ||
    location.pathname.startsWith("/register") ||
    location.pathname.startsWith("/forgot");

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#192B37" }}>
      {!isAuthRoute && <Sidebar />}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {!isAuthRoute && <Header />}
        <div style={{ flex: 1 }}>
          <Routes>
            {/* Public-only */}
            <Route
              path="/login"
              element={
                <PublicOnly>
                  <LoginWrapper />
                </PublicOnly>
              }
            />
            <Route
              path="/register"
              element={
                <PublicOnly>
                  <RegisterWrapper />
                </PublicOnly>
              }
            />
            <Route
              path="/forgot"
              element={
                <PublicOnly>
                  <ForgotWrapper />
                </PublicOnly>
              }
            />

            {/* Private (any logged user) */}
            <Route element={<PrivateRoute />}>
              {/* Admin-only area */}
              <Route element={<RoleRoute allowed={["admin"]} />}>
                <Route path="/" element={<Home />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/documents" element={<MyDocuments />} />
                <Route path="/deleted" element={<RecentlyDeleted />} />
              </Route>

              {/* Normal-only area */}
              <Route element={<RoleRoute allowed={["normal"]} />}>
                <Route path="/forms" element={<Forms />} />
              </Route>

              {/* Shared between roles */}
              <Route path="/transcripts" element={<Transcripts />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Transcripts />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function LoginWrapper() {
  const { login } = useAuth();
  // Hardcode role for now; swap to "normal" for normal users
  return <Login onLoggedIn={(token) => login(token, "normal")} />;
}

function RegisterWrapper() {
  const { login } = useAuth();
  // After register, log in as normal user by default (adjust as desired)
  return <Register onRegistered={(token) => login(token, "normal")} />;
}

function ForgotWrapper() {
  return <Forgot />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </AuthProvider>
  );
}
