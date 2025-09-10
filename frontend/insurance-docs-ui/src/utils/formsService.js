// src/utils/formsService.js
const BASE_URL = "http://127.0.0.1:8000";

export async function fetchForms() {
  const res = await fetch(`${BASE_URL}/forms`, {
    method: "GET",
    headers: { "Accept": "application/json" },
  });

  // FastAPI will still send a JSON body on 4xx/5xx, but guard anyway
  if (!res.ok) {
    let message = `Request failed: ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) message += ` – ${body.detail}`;
    } catch {}
    throw new Error(message);
  }
  return res.json();
}
