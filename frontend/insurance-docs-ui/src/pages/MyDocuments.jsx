import React, { useEffect, useState } from "react";
import { fetchAllDocuments } from "../utils/documentService";
import DocumentItem from "../components/DocumentItem";

export default function MyDocuments() {
  const [docs, setDocs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchAllDocuments();
        setDocs(data || []);
      } catch (e) {
        console.error(e);
        setError("Could not load documents.");
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
        My Documents
      </h2>

      {error && <p style={{ color: "#FF5640" }}>{error}</p>}

      {docs.length === 0 ? (
        <div style={{ color: "#FFFFFF", opacity: 0.7 }}>
          No documents uploaded yet.
        </div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {docs.map((doc) => (
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
