"""Storage stats endpoint — HDD capacity and usage."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Photo
from app.schemas import StorageStats
from app.services.file_manager import get_storage_stats

router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.get("/stats", response_model=StorageStats)
async def storage_stats(db: AsyncSession = Depends(get_db)):
    """Return disk usage statistics and photo count."""
    disk = get_storage_stats()

    # Count photos
    result = await db.execute(select(func.count(Photo.id)))
    photo_count = result.scalar() or 0

    total = disk["total_bytes"]
    used = disk["used_bytes"]
    percentage = (used / total * 100) if total > 0 else 0

    return StorageStats(
        total_bytes=total,
        used_bytes=used,
        free_bytes=disk["free_bytes"],
        photo_count=photo_count,
        percentage_used=round(percentage, 1),
    )
