import { API_BASE } from "../config";

// Upload a file and index it in Chroma
export async function uploadAndIndex(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/upload_and_index`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchAllDocuments(includeDeleted = false) {
  const res = await fetch(`${API_BASE}/documents?include_deleted=${includeDeleted}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchRecentDocuments(limit = 3) {
  const res = await fetch(`${API_BASE}/documents/recent?limit=${limit}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function addInChroma() {
  // first we need to get the paths to all files uploaded
  const response_documents = await fetch(`${API_BASE}/documents`);
  const documents = await response_documents.json();
  let document_paths = []
  documents.forEach((element) => {
    document_paths.push(element.path);
  });

  // now to call the /populate_chroma
  const resp = await fetch(`${API_BASE}/populate_chroma`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paths: document_paths }),
  });

  const data = await resp.json();
  return data.text;
}
