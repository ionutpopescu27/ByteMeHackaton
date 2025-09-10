// src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import PrivateRoute from "./routes/PrivateRoute.jsx";
import PublicOnly from "./routes/PublicOnly.jsx";

// Layout
import Sidebar from "./components/Sidebar";
import Header from "./components/Header"; // remove if you don't have it

// Pages (match your filenames)
import Home from "./pages/Home.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import MyDocuments from "./pages/MyDocuments.jsx";
import RecentlyDeleted from "./pages/RecentlyDeleted.jsx";
import Transcripts from "./pages/Transcripts.jsx";

// ✅ Auth screens live in src/app/(auth) as .js files
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
        {/* if you don't have <Header/>, delete the next line */}
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

            {/* Private */}
            <Route element={<PrivateRoute />}>
              <Route path="/" element={<Home />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/documents" element={<MyDocuments />} />
              <Route path="/deleted" element={<RecentlyDeleted />} />
              <Route path="/transcripts" element={<Transcripts />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Home />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function LoginWrapper() {
  const { login } = useAuth();
  return <Login onLoggedIn={(token) => login(token)} />;
}
function RegisterWrapper() {
  const { login } = useAuth();
  return <Register onRegistered={(token) => login(token)} />;
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
