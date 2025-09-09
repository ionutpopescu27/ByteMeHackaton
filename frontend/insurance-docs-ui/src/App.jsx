import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

// Pages
import Home from "./pages/Home";
import UploadPage from "./pages/UploadPage";
import MyDocuments from "./pages/MyDocuments";
import RecentlyDeleted from "./pages/RecentlyDeleted";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Header />
          <main style={{ padding: "20px" }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/documents" element={<MyDocuments />} />
              <Route path="/deleted" element={<RecentlyDeleted />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
