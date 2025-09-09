import React from "react";
import { Link } from "react-router-dom";
import uploadIcon from "../assets/upload.png";
import settingsIcon from "../assets/settings.png";
import moreIcon from "../assets/more.png";
import notificationsIcon from "../assets/notifications.png";
import trashIcon from "../assets/trash.png";
import documentsIcon from "../assets/documents.png";
import dashboardIcon from "../assets/dashboard.png"; // ✅ NEW ICON

const Sidebar = () => {
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
      {/* 🔼 TOP SECTION: Logo + Upload + Menu Items */}
      <div>
        {/* Logo */}
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

        {/* Upload Button */}
        <Link to="/upload" style={{ textDecoration: "none" }}>
          <button className="upload-button" style={{ marginBottom: "30px" }}>
            <img src={uploadIcon} alt="Upload" style={{ width: "18px", height: "18px" }} />
            <span>Upload</span>
          </button>
        </Link>

        {/* 🏠 Dashboard */}
        <Link to="/" style={{ textDecoration: "none" }}>
          <div className="sidebar-option">
            <img src={dashboardIcon} alt="Dashboard" style={{ width: "20px", height: "20px" }} />
            <span>Dashboard</span>
          </div>
        </Link>

        {/* 📄 My Documents */}
        <Link to="/documents" style={{ textDecoration: "none" }}>
          <div className="sidebar-option">
            <img src={documentsIcon} alt="My Documents" style={{ width: "20px", height: "20px" }} />
            <span>My Documents</span>
          </div>
        </Link>

        {/* 🗑️ Recently Deleted */}
        <Link to="/deleted" style={{ textDecoration: "none" }}>
          <div className="sidebar-option">
            <img src={trashIcon} alt="Recently Deleted" style={{ width: "20px", height: "20px" }} />
            <span>Recently Deleted</span>
          </div>
        </Link>
      </div>

      {/* 🔽 Bottom Row of Icons */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: "40px",
        }}
      >
        <img src={settingsIcon} alt="Settings" style={{ width: "24px", height: "24px", cursor: "pointer" }} />
        <img src={notificationsIcon} alt="Notifications" style={{ width: "24px", height: "24px", cursor: "pointer" }} />
        <img src={moreIcon} alt="More" style={{ width: "24px", height: "24px", cursor: "pointer" }} />
      </div>
    </aside>
  );
};

export default Sidebar;
