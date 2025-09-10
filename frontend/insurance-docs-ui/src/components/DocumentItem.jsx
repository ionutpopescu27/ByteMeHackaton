import React, { useState } from "react";
import fileIcon from "../assets/file.png"; // make sure file.png is in src/assets/

const ORANGE = "#FF5640";
const ORANGE_DARK = "#E44D39";
const TEXT = "#FFFFFF";
const CARD_BORDER = "rgba(255,255,255,0.15)";

export default function DocumentItem({ doc, onClick }) {
  const [hover, setHover] = useState(false);

  const base = {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "12px 16px",
    borderRadius: "10px",
    border: `1px solid ${CARD_BORDER}`,
    backgroundColor: "transparent",
    color: TEXT,
    cursor: "pointer",
    transition:
      "background-color 160ms ease, transform 120ms ease, box-shadow 160ms ease",
    userSelect: "none",
  };

  const hoverStyle = hover
    ? {
        backgroundColor: ORANGE_DARK,
        boxShadow: "0 6px 18px rgba(255, 86, 64, 0.28)",
        transform: "translateY(-1px)",
      }
    : {};

  return (
    <div
      style={{ ...base, ...hoverStyle }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={onClick}
    >
      {/* Left side: icon + name */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          minWidth: 0,
        }}
      >
        <img
          src={fileIcon}
          alt="file"
          style={{ width: 20, height: 20, flexShrink: 0 }}
        />
        <div
          style={{
            fontWeight: 600,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            maxWidth: "300px",
          }}
        >
          {doc?.name || "Untitled.pdf"}
        </div>
      </div>

      {/* Right side: upload date */}
      <div style={{ opacity: 0.9, fontSize: 12, flexShrink: 0 }}>
        {doc?.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : ""}
      </div>
    </div>
  );
}
