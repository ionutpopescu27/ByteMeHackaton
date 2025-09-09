import React, { useEffect, useState } from "react";
import { fetchRecentDocuments } from "../utils/documentService";
import { addInChroma } from "../utils/documentService";
import DocumentItem from "../components/DocumentItem";

export default function Home() {
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");
  const [makingCollection, setMakingCollection] = useState(false);
  const [collectionId, setCollectionId] = useState("");

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


  const handleMakeCollection = async (e) => {
    e.preventDefault();
    try {
      setMakingCollection(true);
      setError("");
      const id = await addInChroma();     // { text: "docs_..." } -> returnează string
      setCollectionId(id);
    } catch (err) {
      setError(err?.message || "Failed to build collection");
    } finally {
      setMakingCollection(false);
    }
  };

  const copyId = async () => {
    try {
      await navigator.clipboard.writeText(collectionId);
    } catch {
    }
  };

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


      <button
        type="button"
        onClick={handleMakeCollection}
        style={{ width: "min(300px, 92vw)" }}
        disabled={makingCollection}
      >
        {makingCollection ? "Building collection..." : "Build Collection from Documents"}
      </button>

      {collectionId && (
        <div style={{ width: "min(900px, 92vw)", display: "flex", gap: 8, alignItems: "center" }}>
          <input
            value={collectionId}
            readOnly
            style={{
              flex: 1,
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #ccc",
              fontFamily: "monospace",
            }}
          />
          <button type="button" onClick={copyId} style={{ padding: "10px 12px", borderRadius: 6 }}>
            Copy
          </button>
        </div>
      )}
    </div>
  );
}
