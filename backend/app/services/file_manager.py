"""File management service — handles chunk assembly, date-based folders, and I/O."""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiofiles

from app.config import settings
from app.utils.hashing import compute_sha256


def _date_folder() -> str:
    """Return a date-based relative path like '2026/04/13'."""
    now = datetime.now(timezone.utc)
    return f"{now.year}/{now.month:02d}/{now.day:02d}"


def get_chunk_dir(upload_id: str) -> Path:
    """Return the temp directory for an upload session's chunks."""
    return Path(settings.temp_path) / upload_id


async def save_chunk(upload_id: str, chunk_index: int, data: bytes) -> Path:
    """Save a single chunk to the temp directory."""
    chunk_dir = get_chunk_dir(upload_id)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunk_path = chunk_dir / f"chunk_{chunk_index:06d}"
    async with aiofiles.open(chunk_path, "wb") as f:
        await f.write(data)
    return chunk_path


async def assemble_chunks(upload_id: str, filename: str, expected_sha256: str) -> tuple[str, str]:
    """
    Assemble all chunks into a final file in the date-based storage folder.

    Returns (relative_path, final_filename).
    Raises ValueError if SHA-256 doesn't match.
    """
    chunk_dir = get_chunk_dir(upload_id)

    # Sort chunks by index
    chunk_files = sorted(chunk_dir.iterdir(), key=lambda p: p.name)

    # Build date-based destination
    date_folder = _date_folder()
    dest_dir = Path(settings.storage_path) / date_folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid collisions
    ext = Path(filename).suffix
    safe_name = Path(filename).stem
    final_name = f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"
    final_path = dest_dir / final_name

    # Assemble
    async with aiofiles.open(final_path, "wb") as out:
        for chunk_file in chunk_files:
            async with aiofiles.open(chunk_file, "rb") as cf:
                while True:
                    block = await cf.read(1024 * 1024)  # 1MB reads
                    if not block:
                        break
                    await out.write(block)

    # Verify SHA-256
    actual_sha = await compute_sha256(final_path)
    if actual_sha != expected_sha256:
        # Cleanup the bad file
        os.remove(final_path)
        raise ValueError(
            f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha}"
        )

    # Cleanup chunks
    cleanup_chunks(upload_id)

    relative_path = f"{date_folder}/{final_name}"
    return relative_path, final_name


def cleanup_chunks(upload_id: str):
    """Remove temporary chunk files for an upload session."""
    chunk_dir = get_chunk_dir(upload_id)
    if chunk_dir.exists():
        for f in chunk_dir.iterdir():
            f.unlink()
        chunk_dir.rmdir()


def get_storage_stats() -> dict:
    """Get disk usage statistics for the storage volume."""
    storage = Path(settings.storage_path)
    try:
        usage = os.statvfs(str(storage))
        total = usage.f_frsize * usage.f_blocks
        free = usage.f_frsize * usage.f_bavail
        used = total - free
    except (OSError, AttributeError):
        # Fallback for systems without statvfs (Windows dev)
        import shutil
        usage = shutil.disk_usage(str(storage))
        total = usage.total
        used = usage.used
        free = usage.free

    return {
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
    }
