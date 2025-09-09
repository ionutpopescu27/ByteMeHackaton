import React, { useEffect, useState } from "react";
import { fetchRecentDocuments } from "../utils/documentService";
import DocumentItem from "../components/DocumentItem";

export default function Home() {
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchRecentDocuments(3);
        setRecent(data || []);
      } catch (e) {
        console.error(e);
        setError("Could not load recently uploaded documents.");
      }
    })();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h2
        style={{
          color: "#FFFFFF",
          marginBottom: 16,
          fontSize: 20,
          fontWeight: 700,
        }}
      >
        Recently Uploaded
      </h2>

      {error && <p style={{ color: "#FF5640" }}>{error}</p>}

      {recent.length === 0 ? (
        <div style={{ color: "#FFFFFF", opacity: 0.7 }}>
          No recent documents.
        </div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {recent.map((doc) => (
            <DocumentItem
              key={doc.id}
              doc={doc}
              onClick={() => {
                console.log("Clicked:", doc.name);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
