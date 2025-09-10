// src/utils/conversationService.js
const API = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

export async function fetchConversationsByPhone(phone) {
  const res = await fetch(`${API}/conv`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: phone }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Failed to fetch conversations (status ${res.status})`);
  }
  return res.json();
}
