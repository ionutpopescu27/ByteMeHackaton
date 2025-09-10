import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import uploadIcon from "../assets/upload.png";
import settingsIcon from "../assets/settings.png";
import moreIcon from "../assets/more.png";
import notificationsIcon from "../assets/notifications.png";
import trashIcon from "../assets/trash.png";
import documentsIcon from "../assets/documents.png";
import dashboardIcon from "../assets/dashboard.png";
import chatIcon from "../assets/chat.png";

const Sidebar = () => {
  const { role, logout } = useAuth(); // NEW: destructure logout too

  const Item = ({ to, icon, label }) => (
    <Link to={to} style={{ textDecoration: "none" }}>
      <div className="sidebar-option" style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <img src={icon} alt={label} style={{ width: 20, height: 20 }} />
        <span style={{ color: "white", fontWeight: 500 }}>{label}</span>
      </div>
    </Link>
  );

  return (
    <aside
      className="sidebar"
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        backgroundColor: "#1F3847",
        padding: "20px",
        width: "250px",
        borderRight: "1px solid #2e4c5c",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div>
        <div
          style={{
            fontSize: "50px",
            fontWeight: "bold",
            color: "white",
            marginBottom: "30px",
          }}
        >
          <strong>InsurAI</strong>
        </div>

        {/* Upload (admin only) */}
        {role === "admin" && (
          <Link to="/upload" style={{ textDecoration: "none" }}>
            <button className="upload-button" style={{ marginBottom: "30px" }}>
              <img src={uploadIcon} alt="Upload" style={{ width: 18, height: 18 }} />
              <span>Upload</span>
            </button>
          </Link>
        )}

        {/* Dashboard (admin only) */}
        {role === "admin" && <Item to="/" icon={dashboardIcon} label="Dashboard" />}

        {/* My Documents (admin only) */}
        {role === "admin" && <Item to="/documents" icon={documentsIcon} label="My Documents" />}

        {/* Transcripts (visible to both roles) */}
        <Item to="/transcripts" icon={chatIcon} label="Transcripts" />

        {/* Forms (normal user only) */}
        {role === "normal" && <Item to="/forms" icon={documentsIcon} label="Forms" />}

        {/* Recently Deleted (admin only) */}
        {role === "admin" && <Item to="/deleted" icon={trashIcon} label="Recently Deleted" />}
      </div>

      {/* Logout button for ALL roles */}
      <button
        onClick={logout}
        style={{
          marginTop: 18,
          background: "transparent",
          border: "1px solid #FF5640",
          color: "#FF5640",
          padding: "8px 10px",
          borderRadius: 8,
          cursor: "pointer",
        }}
      >
        Sign out
      </button>
    </aside>
  );
};

export default Sidebar;
