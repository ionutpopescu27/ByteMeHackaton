import React, { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import bg from "../../assets/voice-ai-dashboard.png"; // keep or swap for any hero image

export default function Login({ onLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  function handleLogin(e) {
    e.preventDefault();
    if (username.trim() && password.length >= 6) {
      // call your API here; on success:
      const fakeToken = "demo-token";
      if (onLoggedIn) onLoggedIn(fakeToken);
      navigate(from, { replace: true });
    } else {
      alert("Enter a username and a 6+ character password.");
    }
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#192B37" }}>
      {/* Left image */}
      <div
        style={{
          flex: 1,
          backgroundImage: `url(${bg})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />

      {/* Right form */}
      <div
        style={{
          flex: 1,
          background: "#192B37",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 40,
        }}
      >
        <div style={{ width: "100%", maxWidth: 360 }}>
          <div
            style={{
              color: "#fff",
              fontSize: 50,
              fontWeight: 800,
              textAlign: "center",
              marginBottom: 12,
              fontFamily: "Helvetica, Arial, sans-serif",
            }}
          >
            InsurAI
          </div>
          <div
            style={{
              color: "#9aa4b2",
              textAlign: "center",
              marginBottom: 24,
              fontFamily: "Helvetica, Arial, sans-serif",
            }}
          >
            Sign in to continue
          </div>

          <form onSubmit={handleLogin}>
            <label
              style={{
                color: "#D1D5D7",
                fontSize: 14,
                marginBottom: 8,
                display: "block",
              }}
            >
              Username
            </label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Your username"
              style={{
                width: "100%",
                background: "#192B37",
                border: "1px solid #FF5640",
                borderRadius: 10,
                padding: "10px 12px",
                color: "#D1D5D7",
                marginBottom: 12,
              }}
            />

            <label
              style={{
                color: "#D1D5D7",
                fontSize: 14,
                marginBottom: 8,
                display: "block",
              }}
            >
              Password
            </label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              type="password"
              style={{
                width: "100%",
                background: "#192B37",
                border: "1px solid #FF5640",
                borderRadius: 10,
                padding: "10px 12px",
                color: "#D1D5D7",
                marginBottom: 12,
              }}
            />

            <button
              type="submit"
              className="upload-button"
              style={{
                width: "100%",
                marginTop: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span style={{ fontWeight: 700 }}>Log In</span>
            </button>
          </form>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 12,
              paddingTop: 16,
              marginTop: 24,
              textAlign: "center",
            }}
          >
            <Link to="/forgot" style={{ color: "#D1D5D7", textDecoration: "underline" }}>
              Forgot password?
            </Link>
            <Link to="/register" style={{ color: "#D1D5D7", textDecoration: "underline" }}>
              Don&apos;t have an account? Register
            </Link>
          </div>

          <div
            style={{
              color: "#667085",
              textAlign: "center",
              marginTop: 12,
              fontFamily: "Helvetica, Arial, sans-serif",
            }}
          >
            By signing in, you agree to the Terms &amp; Privacy.
          </div>
        </div>
      </div>
    </div>
  );
}
