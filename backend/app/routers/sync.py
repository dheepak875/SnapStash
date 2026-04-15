"""Sync / Diff endpoints — intelligent deduplication before upload."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Photo
from app.schemas import DiffRequest, DiffResponse

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/diff", response_model=DiffResponse)
async def compute_diff(req: DiffRequest, db: AsyncSession = Depends(get_db)):
    """
    Client sends a list of files with SHA-256 hashes.
    Server responds with which hashes are already stored (known)
    and which are new (needed).
    """
    client_hashes = {f.sha256 for f in req.files}

    # Query for existing hashes
    result = await db.execute(
        select(Photo.sha256).where(Photo.sha256.in_(list(client_hashes)))
    )
    server_hashes = {row[0] for row in result.all()}

    known = list(server_hashes)
    needed = list(client_hashes - server_hashes)

    return DiffResponse(known=known, needed=needed)


@router.get("/manifest")
async def get_manifest(
    offset: int = 0,
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
):
    """Return a paginated list of all stored file hashes."""
    result = await db.execute(
        select(Photo.sha256, Photo.original_name, Photo.size_bytes)
        .order_by(Photo.uploaded_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    return {
        "files": [
            {"sha256": r[0], "filename": r[1], "size": r[2]}
            for r in rows
        ],
        "offset": offset,
        "limit": limit,
        "count": len(rows),
    }
