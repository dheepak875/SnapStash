"""Welcome page and QR code endpoints."""

import io
import socket

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

from app.config import settings
from app.database import get_db
from app.models import Photo
from app.schemas import ApplianceStatus
from app.services.file_manager import get_storage_stats

router = APIRouter(prefix="/api/welcome", tags=["welcome"])


@router.get("/qr")
async def get_qr_code():
    """Generate a QR code PNG containing the app URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(settings.base_url)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="#4F8EF7",
        back_color="#0F172A",
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@router.get("/status", response_model=ApplianceStatus)
async def appliance_status(db: AsyncSession = Depends(get_db)):
    """Return appliance health and connection info."""
    disk = get_storage_stats()

    result = await db.execute(select(func.count(Photo.id)))
    photo_count = result.scalar() or 0

    # Check if storage is connected
    from pathlib import Path
    storage_connected = Path(settings.storage_path).exists()

    hostname = socket.gethostname()

    return ApplianceStatus(
        storage_connected=storage_connected,
        photo_count=photo_count,
        total_bytes=disk["total_bytes"],
        used_bytes=disk["used_bytes"],
        free_bytes=disk["free_bytes"],
        hostname=hostname,
        app_url=settings.base_url,
    )
