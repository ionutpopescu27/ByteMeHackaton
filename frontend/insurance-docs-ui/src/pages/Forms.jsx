// src/pages/Forms.jsx
import React, { useEffect, useMemo, useState } from "react";
import { fetchForms } from "../utils/formsService";

function EmptyState() {
  return (
    <div style={{ color: "#FFFFFF", opacity: 0.7 }}>
      No personalized forms yet.
    </div>
  );
}

function Row({ form, onToggle, expanded }) {
  const created = useMemo(() => {
    try {
      return new Date(form.created_at).toLocaleString();
    } catch {
      return form.created_at;
    }
  }, [form.created_at]);

  const qCount = form.questions?.length ?? 0;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(form, null, 2));
    } catch {}
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(form, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const shortId = String(form.id).slice(0, 8);
    a.download = `form-${shortId}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const convLabel =
    form?.conversation?.label ||
    form?.conversation?.phone_number ||
    "Conversation";

  return (
    <div
      onClick={onToggle}
      className="forms-row"
      style={{
        cursor: "pointer",
        background: expanded ? "rgba(255,255,255,0.04)" : "transparent",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 10,
        padding: 14,
        transition: "transform .15s ease, background .2s ease, box-shadow .2s ease",
        boxShadow: expanded ? "0 10px 22px rgba(0,0,0,0.35)" : "none",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.boxShadow = "0 10px 22px rgba(0,0,0,0.35)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        if (!expanded) e.currentTarget.style.boxShadow = "none";
      }}
    >
      {/* Top row (summary) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr auto",
          gap: 12,
          alignItems: "center",
        }}
      >
        <div style={{ minWidth: 0 }}>
          <div
            style={{
              color: "#FFFFFF",
              fontWeight: 700,
              fontSize: 16,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
            title={`Form ${form.id}`}
          >
            {convLabel} • {qCount} question{qCount === 1 ? "" : "s"}
          </div>
          <div style={{ color: "#9aa4b2", marginTop: 4, fontSize: 13 }}>
            {created} • locale: {form.locale || "—"}
          </div>
        </div>

        <div
          onClick={(e) => e.stopPropagation()}
          style={{ display: "flex", gap: 8 }}
        >
          <button
            type="button"
            onClick={handleCopy}
            style={{
              borderRadius: 8,
              border: "1px solid #FF5640",
              background: "transparent",
              color: "#D1D5D7",
              padding: "8px 10px",
            }}
          >
            Copy JSON
          </button>
          <button
            type="button"
            onClick={handleDownload}
            style={{
              borderRadius: 8,
              background: "#FF5640",
              color: "white",
              border: 0,
              padding: "8px 10px",
              fontWeight: 700,
            }}
          >
            Download
          </button>
        </div>
      </div>

      {/* Expanded: questions list */}
      {expanded && (
        <div style={{ marginTop: 12 }}>
          <ol style={{ margin: 0, paddingLeft: 20, color: "#D1D5D7" }}>
            {(form.questions || []).map((q, idx) => (
              <li key={idx} style={{ marginBottom: 8, lineHeight: 1.4 }}>
                {q}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export default function Forms() {
  const [forms, setForms] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        setErr("");
        setLoading(true);
        const data = await fetchForms();
        if (!isMounted) return;
        // Ensure array
        setForms(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!isMounted) return;
        setErr(e?.message || "Failed to load forms");
      } finally {
        if (isMounted) setLoading(false);
      }
    })();
    return () => {
      isMounted = false;
    };
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
        Personalized Forms
      </h2>

      {err && <div style={{ color: "#FF7B6B", marginBottom: 12 }}>{err}</div>}
      {loading && <div style={{ color: "#D1D5D7" }}>Loading…</div>}

      {!loading && forms.length === 0 && <EmptyState />}

      {!loading && forms.length > 0 && (
        <div style={{ display: "grid", gap: 12 }}>
          {forms.map((f) => (
            <Row
              key={f.id}
              form={f}
              expanded={expandedId === f.id}
              onToggle={() =>
                setExpandedId((curr) => (curr === f.id ? null : f.id))
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
