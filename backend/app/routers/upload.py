"""Chunked upload endpoints — init, upload chunk, complete, abort."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path as PathParam
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import UploadSession, Photo
from app.schemas import (
    UploadInitRequest,
    UploadInitResponse,
    ChunkUploadResponse,
    UploadCompleteResponse,
)
from app.services.file_manager import save_chunk, assemble_chunks, cleanup_chunks

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/init", response_model=UploadInitResponse)
async def init_upload(req: UploadInitRequest, db: AsyncSession = Depends(get_db)):
    """Initialize a new chunked upload session."""
    session = UploadSession(
        filename=req.filename,
        total_chunks=req.total_chunks,
        total_size=req.total_size,
        sha256=req.sha256,
        mime_type=req.mime_type,
        status="pending",
    )
    db.add(session)
    await db.flush()
    return UploadInitResponse(upload_id=session.id, status="pending")


@router.post("/{upload_id}/chunk/{chunk_index}", response_model=ChunkUploadResponse)
async def upload_chunk(
    upload_id: str = PathParam(...),
    chunk_index: int = PathParam(..., ge=0),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a single chunk of a file."""
    # Verify session exists
    result = await db.execute(
        select(UploadSession).where(UploadSession.id == upload_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")
    if session.status != "pending":
        raise HTTPException(status_code=400, detail=f"Upload session is {session.status}")
    if chunk_index >= session.total_chunks:
        raise HTTPException(status_code=400, detail="Chunk index out of range")

    # Read and save the chunk
    data = await file.read()
    await save_chunk(upload_id, chunk_index, data)

    # Update received count
    session.received_chunks = chunk_index + 1
    await db.flush()

    return ChunkUploadResponse(
        upload_id=upload_id,
        chunk_index=chunk_index,
        received_chunks=session.received_chunks,
        total_chunks=session.total_chunks,
    )


@router.post("/{upload_id}/complete", response_model=UploadCompleteResponse)
async def complete_upload(
    upload_id: str = PathParam(...),
    db: AsyncSession = Depends(get_db),
):
    """Assemble chunks and finalize the upload."""
    result = await db.execute(
        select(UploadSession).where(UploadSession.id == upload_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")
    if session.status != "pending":
        raise HTTPException(status_code=400, detail=f"Upload session is {session.status}")

    try:
        relative_path, final_name = await assemble_chunks(
            upload_id, session.filename, session.sha256
        )
    except ValueError as e:
        session.status = "failed"
        await db.flush()
        raise HTTPException(status_code=422, detail=str(e))

    # Create photo record
    photo = Photo(
        filename=final_name,
        original_name=session.filename,
        sha256=session.sha256,
        size_bytes=session.total_size,
        mime_type=session.mime_type,
        relative_path=relative_path,
    )
    db.add(photo)

    session.status = "complete"
    await db.flush()

    return UploadCompleteResponse(
        upload_id=upload_id,
        filename=final_name,
        sha256=session.sha256,
        size_bytes=session.total_size,
        status="complete",
    )


@router.delete("/{upload_id}")
async def abort_upload(
    upload_id: str = PathParam(...),
    db: AsyncSession = Depends(get_db),
):
    """Abort and clean up a failed/cancelled upload."""
    result = await db.execute(
        select(UploadSession).where(UploadSession.id == upload_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")

    cleanup_chunks(upload_id)
    session.status = "failed"
    await db.flush()

    return {"status": "aborted", "upload_id": upload_id}
