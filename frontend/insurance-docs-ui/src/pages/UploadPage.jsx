import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadAndIndex } from "../utils/documentService";

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleDrop = (e) => { e.preventDefault(); setFile(e.dataTransfer.files[0]); };
  const handleDragOver = (e) => e.preventDefault();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    try {
      setBusy(true);
      setError("");
      await uploadAndIndex(file);
      navigate("/"); // back to Dashboard
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ flex: 1, display: "flex", justifyContent: "flex-start", alignItems: "center", flexDirection: "column", marginTop: "60px" }}>
      <form onSubmit={handleSubmit} style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          style={{
            width: "min(900px, 92vw)",
            height: "min(520px, 60vh)",
            borderRadius: "12px",
            backgroundColor: "#1F3847",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            cursor: "pointer",
            padding: 24,
            boxSizing: "border-box",
          }}
        >
          <div style={{ width: 80, height: 80, borderRadius: "50%", border: "3px solid #FF5640", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
            <span style={{ fontSize: 32, color: "#FF5640" }}>↑</span>
          </div>

          {file ? <p style={{ fontSize: 16 }}>{file.name}</p> : <p style={{ fontSize: 18 }}>Drag & drop a PDF here, or click below</p>}

          <label style={{ marginTop: 20, backgroundColor: "#FF5640", color: "white", padding: "12px 24px", borderRadius: 6, fontWeight: "bold", cursor: "pointer", fontSize: 16 }}>
            Choose File
            <input type="file" accept="application/pdf" onChange={handleFileChange} style={{ display: "none" }} />
          </label>
        </div>

        {error && <p style={{ color: "#FF5640" }}>{error}</p>}

        {file && (
          <button type="submit" className="upload-button" style={{ width: "min(300px, 92vw)" }} disabled={busy}>
            {busy ? "Uploading..." : "Upload"}
          </button>
        )}
      </form>
    </div>
  );
};

export default UploadPage;
