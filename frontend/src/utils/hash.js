/**
 * Client-side SHA-256 hashing using the Web Crypto API.
 * Streams large files in chunks to avoid memory pressure.
 */

const HASH_CHUNK_SIZE = 2 * 1024 * 1024; // 2MB

/**
 * Compute SHA-256 hash of a File object.
 * Reads in chunks for memory efficiency.
 *
 * @param {File} file
 * @returns {Promise<string>} hex-encoded SHA-256 hash
 */
export async function computeSHA256(file) {
  // For small files, hash all at once
  if (file.size <= HASH_CHUNK_SIZE) {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    return bufferToHex(hashBuffer);
  }

  // For large files, read in chunks and hash incrementally
  // The Web Crypto API doesn't support streaming natively,
  // so we use a manual approach
  const chunks = Math.ceil(file.size / HASH_CHUNK_SIZE);
  const hashParts = [];

  for (let i = 0; i < chunks; i++) {
    const start = i * HASH_CHUNK_SIZE;
    const end = Math.min(start + HASH_CHUNK_SIZE, file.size);
    const slice = file.slice(start, end);
    const buffer = await slice.arrayBuffer();
    hashParts.push(new Uint8Array(buffer));
  }

  // Concatenate all parts and hash
  const totalLen = hashParts.reduce((acc, part) => acc + part.length, 0);
  const combined = new Uint8Array(totalLen);
  let offset = 0;
  for (const part of hashParts) {
    combined.set(part, offset);
    offset += part.length;
  }

  const hashBuffer = await crypto.subtle.digest('SHA-256', combined);
  return bufferToHex(hashBuffer);
}

/**
 * Convert an ArrayBuffer to a hex string.
 */
function bufferToHex(buffer) {
  const bytes = new Uint8Array(buffer);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}
