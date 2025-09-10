import React, { useEffect, useState } from "react";
import { fetchRecentDocuments, addInChroma } from "../utils/documentService";
import DocumentItem from "../components/DocumentItem";

const BG = "#192B37";
const ORANGE = "#FF5640";
const ORANGE_DARK = "#E44D39";
const TEXT = "#FFFFFF";
const BORDER = "rgba(255,255,255,0.15)";

export default function Home() {
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");
  const [makingCollection, setMakingCollection] = useState(false);
  const [collectionId, setCollectionId] = useState("");

  // Hover states for buttons
  const [hoverBuild, setHoverBuild] = useState(false);
  const [hoverCopy, setHoverCopy] = useState(false);

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
      const id = await addInChroma(); // returns collectionId string
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
    } catch {}
  };

  // Shared styles
  const buttonBase = {
    backgroundColor: hoverBuild ? ORANGE_DARK : ORANGE,
    color: TEXT,
    padding: "12px 16px",
    border: "none",
    borderRadius: 10,
    cursor: makingCollection ? "not-allowed" : "pointer",
    fontWeight: 700,
    transition: "background-color 150ms ease, transform 120ms ease, box-shadow 160ms ease",
    boxShadow: hoverBuild ? "0 6px 18px rgba(255,86,64,0.28)" : "none",
    transform: hoverBuild ? "translateY(-1px)" : "none",
    width: "min(320px, 92vw)",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    opacity: makingCollection ? 0.75 : 1,
  };

  const inputBase = {
    flex: 1,
    padding: "12px 14px",
    borderRadius: 10,
    border: `1px solid ${BORDER}`,
    backgroundColor: "rgba(255,255,255,0.06)",
    color: TEXT,
    outline: "none",
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  };

  const copyBtnBase = {
    backgroundColor: hoverCopy ? ORANGE_DARK : ORANGE,
    color: TEXT,
    border: "none",
    borderRadius: 10,
    padding: "12px 14px",
    fontWeight: 700,
    cursor: "pointer",
    transition: "background-color 150ms ease, transform 120ms ease, box-shadow 160ms ease",
    boxShadow: hoverCopy ? "0 6px 18px rgba(255,86,64,0.28)" : "none",
    transform: hoverCopy ? "translateY(-1px)" : "none",
    whiteSpace: "nowrap",
  };

  return (
    <div style={{ padding: 24, backgroundColor: BG, minHeight: "100%" }}>
      <h2
        style={{
          color: TEXT,
          marginBottom: 16,
          fontSize: 20,
          fontWeight: 700,
        }}
      >
        Recently Uploaded
      </h2>

      {error && <p style={{ color: ORANGE }}>{error}</p>}

      {recent.length === 0 ? (
        <div style={{ color: TEXT, opacity: 0.7 }}>No recent documents.</div>
      ) : (
        <div style={{ display: "grid", gap: 12, marginBottom: 24 }}>
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

      {/* Build Collection button */}
      <button
        type="button"
        onClick={handleMakeCollection}
        style={buttonBase}
        disabled={makingCollection}
        onMouseEnter={() => setHoverBuild(true)}
        onMouseLeave={() => setHoverBuild(false)}
      >
        {makingCollection ? "Building collection..." : "Build Collection from Documents"}
      </button>

      {/* Collection output field + Copy button */}
      {collectionId && (
        <div
          style={{
            width: "min(900px, 92vw)",
            display: "flex",
            gap: 10,
            alignItems: "center",
            marginTop: 16,
          }}
        >
          <input
            value={collectionId}
            readOnly
            style={inputBase}
            aria-label="Collection ID"
          />
          <button
            type="button"
            onClick={copyId}
            style={copyBtnBase}
            onMouseEnter={() => setHoverCopy(true)}
            onMouseLeave={() => setHoverCopy(false)}
          >
            Copy
          </button>
        </div>
      )}
    </div>
  );
}
