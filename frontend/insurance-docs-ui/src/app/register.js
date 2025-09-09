import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Register({ onRegistered }) {
  const navigate = useNavigate();

  const [type, setType] = useState("client"); // client | company

  // shared
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  // client
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  // company
  const [companyName, setCompanyName] = useState("");
  const [registrationNo, setRegistrationNo] = useState("");
  const [contactPerson, setContactPerson] = useState("");

  const emailError = useMemo(() => {
    if (!email) return "";
    return /[^\s@]+@[^\s@]+\.[^\s@]+/.test(email.trim()) ? "" : "Enter a valid email.";
  }, [email]);

  const passwordError = useMemo(() => {
    if (!password) return "";
    return password.length >= 6 ? "" : "Password must be at least 6 characters.";
  }, [password]);

  const confirmError = useMemo(() => {
    if (!confirm) return "";
    return confirm === password ? "" : "Passwords do not match.";
  }, [confirm, password]);

  function validate() {
    if (!email.trim() || !password || !confirm) return false;
    if (emailError || passwordError || confirmError) return false;

    if (type === "client") {
      if (!username.trim() || !firstName.trim() || !lastName.trim()) return false;
    } else {
      if (!companyName.trim() || !registrationNo.trim() || !contactPerson.trim())
        return false;
    }
    return true;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) {
      alert("Please complete all required fields correctly.");
      return;
    }
    // call your API here; on success:
    const fakeToken = "new-user-token";
    if (onRegistered) onRegistered(fakeToken);
    navigate("/", { replace: true });
  }

  const inputStyle = {
    width: "100%",
    background: "#192B37",
    border: "1px solid #FF5640",
    borderRadius: 10,
    padding: "10px 12px",
    color: "white",
    marginBottom: 8,
  };

  const labelStyle = {
    color: "#d6dbe1",
    marginBottom: 6,
    marginTop: 8,
    display: "block",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#192B37",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        padding: "34px 16px",
      }}
    >
      <div style={{ width: "100%", maxWidth: 680 }}>
        <h1
          style={{
            color: "#fff",
            fontWeight: 800,
            textAlign: "center",
            margin: 0,
            fontSize: 36,
          }}
        >
          InsurAI
        </h1>
        <p style={{ color: "#9aa4b2", textAlign: "center", marginTop: 8 }}>
          Create your account
        </p>

        {/* Account type */}
        <label style={labelStyle}>Account Type *</label>
        <div
          style={{
            display: "flex",
            border: "1px solid #FF5640",
            overflow: "hidden",
            borderRadius: 8,
            marginBottom: 10,
          }}
        >
          <button
            type="button"
            onClick={() => setType("client")}
            style={{
              flex: 1,
              background: type === "client" ? "#FF5640" : "#192B37",
              color: type === "client" ? "white" : "#9aa4b2",
              fontWeight: type === "client" ? 700 : 600,
              padding: "10px 0",
              border: "none",
              cursor: "pointer",
            }}
          >
            Client
          </button>
          <button
            type="button"
            onClick={() => setType("company")}
            style={{
              flex: 1,
              background: type === "company" ? "#FF5640" : "#192B37",
              color: type === "company" ? "white" : "#9aa4b2",
              fontWeight: type === "company" ? 700 : 600,
              padding: "10px 0",
              border: "none",
              cursor: "pointer",
              borderLeft: "1px solid #FF5640",
            }}
          >
            Company
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {type === "client" && (
            <>
              <label style={labelStyle}>Username *</label>
              <input
                style={inputStyle}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Your username"
              />

              <div style={{ display: "grid", gap: 10, gridTemplateColumns: "1fr 1fr" }}>
                <div>
                  <label style={labelStyle}>First Name *</label>
                  <input
                    style={inputStyle}
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="John"
                  />
                </div>
                <div>
                  <label style={labelStyle}>Last Name *</label>
                  <input
                    style={inputStyle}
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Doe"
                  />
                </div>
              </div>
            </>
          )}

          {type === "company" && (
            <>
              <label style={labelStyle}>Company Name *</label>
              <input
                style={inputStyle}
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Acme Inc."
              />

              <div style={{ display: "grid", gap: 10, gridTemplateColumns: "1fr 1fr" }}>
                <div>
                  <label style={labelStyle}>Registration Number *</label>
                <input
                    style={inputStyle}
                    value={registrationNo}
                    onChange={(e) => setRegistrationNo(e.target.value)}
                    placeholder="RO12345678"
                  />
                </div>
                <div>
                  <label style={labelStyle}>Contact Person *</label>
                  <input
                    style={inputStyle}
                    value={contactPerson}
                    onChange={(e) => setContactPerson(e.target.value)}
                    placeholder="Jane Doe"
                  />
                </div>
              </div>
            </>
          )}

          {/* Shared */}
          <label style={labelStyle}>Email *</label>
          <input
            style={{
              ...inputStyle,
              borderColor: emailError ? "#e24d4d" : "#FF5640",
            }}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            type="email"
          />
          {!!emailError && (
            <div style={{ color: "#ff7b7b", marginBottom: 6 }}>{emailError}</div>
          )}

          <label style={labelStyle}>Password *</label>
          <input
            style={{
              ...inputStyle,
              borderColor: passwordError ? "#e24d4d" : "#FF5640",
            }}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Minimum 6 characters"
            type="password"
          />
          {!!passwordError && (
            <div style={{ color: "#ff7b7b", marginBottom: 6 }}>{passwordError}</div>
          )}

          <label style={labelStyle}>Confirm Password *</label>
          <input
            style={{
              ...inputStyle,
              borderColor: confirmError ? "#e24d4d" : "#FF5640",
            }}
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="Re-enter password"
            type="password"
          />
          {!!confirmError && (
            <div style={{ color: "#ff7b7b", marginBottom: 6 }}>{confirmError}</div>
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
            <span style={{ fontWeight: 700 }}>Create Account</span>
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
            Back to Login
          </Link>
        </form>
      </div>
    </div>
  );
}
