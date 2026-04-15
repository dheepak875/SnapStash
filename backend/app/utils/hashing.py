"""SHA-256 hashing utilities for file integrity verification."""

import hashlib
from pathlib import Path

import aiofiles

HASH_CHUNK_SIZE = 8192


async def compute_sha256(filepath: str | Path) -> str:
    """Compute SHA-256 hash of a file by streaming it in chunks."""
    sha = hashlib.sha256()
    async with aiofiles.open(filepath, "rb") as f:
        while True:
            chunk = await f.read(HASH_CHUNK_SIZE)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of in-memory bytes."""
    return hashlib.sha256(data).hexdigest()
