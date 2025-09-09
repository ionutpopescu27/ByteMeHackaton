// src/pages/Transcripts.jsx
import React, { useState } from "react";
import { fetchConversationsByPhone } from "../utils/conversationService";

const BG = "#192B37";
const ORANGE = "#FF5640";
const ORANGE_DARK = "#E44D39";
const TEXT = "#FFFFFF";
const BORDER = "rgba(255,255,255,0.15)";

const labelInfo = (label, endedAt) => {
  const map = {
    resolved: { text: "Resolved", bg: "#dcfce7", fg: "#166534" },
    escalated_website: { text: "Escalated · Website", bg: "#dbeafe", fg: "#1e40af" },
    escalated_human: { text: "Escalated · Human", bg: "#fee2e2", fg: "#991b1b" },
    open: { text: "Open", bg: "#fef3c7", fg: "#92400e" },
  };
  const key = label || (!endedAt ? "open" : "resolved");
  return map[key] || map.open;
};

function SectionCard({ title, children, right }) {
  return (
    <div
      style={{
        border: `1px solid ${BORDER}`,
        borderRadius: 12,
        background: "rgba(255,255,255,0.04)",
        padding: 16,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <h3 style={{ margin: 0, color: TEXT, fontSize: 16, fontWeight: 700 }}>
          {title}
        </h3>
        {right}
      </div>
      {children}
    </div>
  );
}

function ConversationHeader({ conv, expanded, toggle }) {
  const started = conv?.started_at ? new Date(conv.started_at).toLocaleString() : "";
  const ended = conv?.ended_at ? new Date(conv.ended_at).toLocaleString() : "";
  const count = (conv?.messages || []).length;
  const info = labelInfo(conv.label, conv.ended_at);

  return (
    <button
      onClick={toggle}
      style={{
        width: "100%",
        textAlign: "left",
        backgroundColor: expanded ? ORANGE_DARK : "transparent",
        color: TEXT,
        border: `1px solid ${BORDER}`,
        borderRadius: 10,
        padding: "12px 14px",
        cursor: "pointer",
        transition: "background-color 150ms ease, transform 120ms ease, box-shadow 160ms ease",
        boxShadow: expanded ? "0 6px 18px rgba(255,86,64,0.28)" : "none",
        transform: expanded ? "translateY(-1px)" : "none",
      }}
      onMouseEnter={(e) => {
        if (!expanded) e.currentTarget.style.backgroundColor = ORANGE;
      }}
      onMouseLeave={(e) => {
        if (!expanded) e.currentTarget.style.backgroundColor = "transparent";
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ fontWeight: 700 }}>
            {started} {!!ended && <> → {ended}</>} — {count} message{count === 1 ? "" : "s"}
          </div>
          <span
            style={{
              alignSelf: "center",
              display: "inline-block",
              padding: "2px 10px",
              borderRadius: 999,
              fontSize: 12,
              fontWeight: 600,
              background: info.bg,
              color: info.fg,
            }}
            title={conv.label || (!conv.ended_at ? "open" : "resolved")}
          >
            {info.text}
          </span>
        </div>
        <div style={{ opacity: 0.9 }}>{expanded ? "Hide" : "View"}</div>
      </div>
    </button>
  );
}
function MessageBubble({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginTop: 8,
      }}
    >
      <div
        style={{
          maxWidth: "760px",
          borderRadius: 12,
          padding: "10px 12px",
          background: isUser ? ORANGE : "rgba(255,255,255,0.06)",
          color: TEXT,
          border: `1px solid ${isUser ? "transparent" : BORDER}`,
          boxShadow: isUser ? "0 6px 18px rgba(255,86,64,0.28)" : "none",
          whiteSpace: "pre-wrap",
        }}
      >
        <div style={{ opacity: 0.85, fontSize: 12, marginBottom: 4 }}>
          {new Date(msg.created_at).toLocaleString()} · {isUser ? "You" : "Bot"}
        </div>
        <div style={{ fontWeight: 600, lineHeight: 1.45 }}>{msg.text}</div>

        {/* Optional: show source doc + page when present */}
        {(msg.path_df || msg.number_page != null) && (
          <div
            style={{
              marginTop: 8,
              fontSize: 12,
              opacity: 0.9,
              borderTop: `1px dashed ${BORDER}`,
              paddingTop: 6,
            }}
          >
            {msg.path_df ? <div>Source: {msg.path_df}</div> : null}
            {msg.number_page != null ? <div>Page: {msg.number_page}</div> : null}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Transcripts() {
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState({}); // { [conv.id]: boolean }

  const [hoverFetch, setHoverFetch] = useState(false);

  const buttonStyles = {
    backgroundColor: hoverFetch ? ORANGE_DARK : ORANGE,
    color: TEXT,
    padding: "12px 16px",
    border: "none",
    borderRadius: 10,
    cursor: loading ? "not-allowed" : "pointer",
    fontWeight: 700,
    transition: "background-color 150ms ease, transform 120ms ease, box-shadow 160ms ease",
    boxShadow: hoverFetch ? "0 6px 18px rgba(255,86,64,0.28)" : "none",
    transform: hoverFetch ? "translateY(-1px)" : "none",
    opacity: loading ? 0.75 : 1,
    whiteSpace: "nowrap",
  };

  const inputStyles = {
    flex: 1,
    minWidth: 280,
    padding: "12px 14px",
    borderRadius: 10,
    border: `1px solid ${BORDER}`,
    backgroundColor: "rgba(255,255,255,0.06)",
    color: TEXT,
    outline: "none",
    fontWeight: 600,
  };

  const fetchData = async (e) => {
    e?.preventDefault?.();
    setError("");
    setConversations([]);
    setLoading(true);
    try {
      const data = await fetchConversationsByPhone(phone.trim());
      setConversations(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err?.message || "Failed to fetch conversations");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, background: BG, minHeight: "100%" }}>
      <h2 style={{ color: TEXT, marginBottom: 16, fontSize: 20, fontWeight: 700 }}>
        Chatbot Transcripts
      </h2>

      <SectionCard
        title="Find conversations by phone number"
        right={null}
      >
        <form
          onSubmit={fetchData}
          style={{ display: "flex", gap: 10, flexWrap: "wrap" }}
        >
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+407xxxxxxxx"
            aria-label="Phone number"
            style={inputStyles}
          />
          <button
            type="submit"
            disabled={loading || !phone.trim()}
            style={buttonStyles}
            onMouseEnter={() => setHoverFetch(true)}
            onMouseLeave={() => setHoverFetch(false)}
          >
            {loading ? "Loading..." : "Fetch Conversations"}
          </button>
        </form>
        {error && <div style={{ color: ORANGE, marginTop: 10 }}>{error}</div>}
      </SectionCard>

      <div style={{ height: 16 }} />

      <SectionCard title="Results">
        {conversations.length === 0 ? (
          <div style={{ color: TEXT, opacity: 0.7 }}>No results yet.</div>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {conversations.map((c) => {
              (() => {
                const info = labelInfo(c.label, c.ended_at);
                return (
                  <span
                    style={{
                      alignSelf: "start",
                      display: "inline-block",
                      padding: "2px 10px",
                      borderRadius: 999,
                      fontSize: 12,
                      fontWeight: 600,
                      background: info.bg,
                      color: info.fg,
                    }}
                    title={c.label || (!c.ended_at ? "open" : "resolved")}
                  >
                    {info.text}
                  </span>
                );
              })()
              const isOpen = !!expanded[c.id];
              return (
                <div key={c.id} style={{ display: "grid", gap: 10 }}>
                  <ConversationHeader
                    conv={c}
                    expanded={isOpen}
                    toggle={() =>
                      setExpanded((s) => ({ ...s, [c.id]: !s[c.id] }))
                    }
                  />

                  {isOpen && (
                    <div style={{ paddingLeft: 6 }}>
                      {(c.messages || []).map((m) => (
                        <MessageBubble key={m.id} msg={m} />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </SectionCard>
    </div>
  );
}
