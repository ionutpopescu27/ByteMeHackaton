import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Forgot() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const emailError = useMemo(() => {
    if (!email) return "";
    return /[^\s@]+@[^\s@]+\.[^\s@]+/.test(email.trim())
      ? ""
      : "Enter a valid email.";
  }, [email]);

  function handleSubmit(e) {
    e.preventDefault();
    if (!email.trim() || emailError) {
      alert("Please enter a valid email address.");
      return;
    }
    // TODO: call your backend to send reset link
    alert(`If an account exists for ${email}, a reset link has been sent.`);
    navigate("/login", { replace: true });
  }

  const inputStyle = {
    width: "100%",
    background: "#192B37",
    border: `1px solid ${emailError ? "#e24d4d" : "#FF5640"}`,
    borderRadius: 10,
    padding: "10px 12px",
    color: "white",
    marginBottom: 8,
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#192B37",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        padding: "48px 16px",
      }}
    >
      <div style={{ width: "100%", maxWidth: 680 }}>
        <h1
          style={{
            color: "white",
            fontWeight: 800,
            textAlign: "center",
            margin: 0,
            fontSize: 36,
          }}
        >
          InsurAI
        </h1>

        <p style={{ color: "#9aa4b2", textAlign: "center", marginTop: 4 }}>
          Forgot your password?
        </p>
        <p
          style={{
            color: "#9aa4b2",
            textAlign: "center",
            marginTop: 8,
            marginBottom: 16,
          }}
        >
          Enter the email linked to your account and we’ll send instructions to
          reset your password.
        </p>

        <form onSubmit={handleSubmit} style={{ maxWidth: 520, margin: "0 auto" }}>
          <label
            style={{
              color: "#d6dbe1",
              marginBottom: 6,
              marginTop: 8,
              display: "block",
            }}
          >
            Email *
          </label>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
          />
          {!!emailError && (
            <div style={{ color: "#ff7b7b", marginBottom: 6 }}>{emailError}</div>
          )}

          <button
            type="submit"
            className="upload-button"
            style={{
              width: "100%",
              marginTop: 20,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ fontWeight: 700 }}>Send reset link</span>
          </button>

          <Link
            to="/login"
            style={{
              display: "inline-block",
              textAlign: "center",
              width: "100%",
              marginTop: 10,
              padding: "10px 0",
              borderRadius: 10,
              border: "1px solid #FF5640",
              color: "#9aa4b2",
              fontWeight: 600,
              textDecoration: "none",
            }}
          >
            Back to login
          </Link>
        </form>
      </div>
    </div>
  );
}
