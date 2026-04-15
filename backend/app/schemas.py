"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel


# --- Upload ---

class UploadInitRequest(BaseModel):
    filename: str
    total_chunks: int
    total_size: int
    sha256: str
    mime_type: str | None = None


class UploadInitResponse(BaseModel):
    upload_id: str
    status: str


class ChunkUploadResponse(BaseModel):
    upload_id: str
    chunk_index: int
    received_chunks: int
    total_chunks: int


class UploadCompleteResponse(BaseModel):
    upload_id: str
    filename: str
    sha256: str
    size_bytes: int
    status: str


# --- Sync / Diff ---

class FileInfo(BaseModel):
    filename: str
    sha256: str
    size: int


class DiffRequest(BaseModel):
    files: list[FileInfo]


class DiffResponse(BaseModel):
    known: list[str]    # SHA-256 hashes already on server
    needed: list[str]   # SHA-256 hashes the server needs


# --- Storage ---

class StorageStats(BaseModel):
    total_bytes: int
    used_bytes: int
    free_bytes: int
    photo_count: int
    percentage_used: float


# --- Welcome ---

class ApplianceStatus(BaseModel):
    storage_connected: bool
    photo_count: int
    total_bytes: int
    used_bytes: int
    free_bytes: int
    hostname: str
    app_url: str
