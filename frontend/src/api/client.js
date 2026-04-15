/**
 * SnapStash API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = '/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res;
}

async function json(path, options = {}) {
  const res = await request(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  return res.json();
}

// --- Upload ---

export async function initUpload({ filename, totalChunks, totalSize, sha256, mimeType }) {
  return json('/upload/init', {
    method: 'POST',
    body: JSON.stringify({
      filename,
      total_chunks: totalChunks,
      total_size: totalSize,
      sha256,
      mime_type: mimeType,
    }),
  });
}

export async function uploadChunk(uploadId, chunkIndex, blob) {
  const formData = new FormData();
  formData.append('file', blob, `chunk_${chunkIndex}`);

  const res = await request(`/upload/${uploadId}/chunk/${chunkIndex}`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function completeUpload(uploadId) {
  return json(`/upload/${uploadId}/complete`, { method: 'POST' });
}

export async function abortUpload(uploadId) {
  return json(`/upload/${uploadId}`, { method: 'DELETE' });
}

// --- Sync / Diff ---

export async function getDiff(files) {
  return json('/sync/diff', {
    method: 'POST',
    body: JSON.stringify({ files }),
  });
}

// --- Storage ---

export async function getStorageStats() {
  return json('/storage/stats');
}

// --- Welcome ---

export async function getQRCodeUrl() {
  const res = await request('/welcome/qr');
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function getApplianceStatus() {
  return json('/welcome/status');
}
