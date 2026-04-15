"""SnapStash — FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings, ensure_directories
from app.database import init_db
from app.routers import upload, sync, storage, welcome


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # Startup
    ensure_directories()
    await init_db()
    print(f"🚀 SnapStash v{settings.app_version} ready")
    print(f"📁 Storage: {settings.storage_path}")
    print(f"🗄️  Database: {settings.db_path}")
    yield
    # Shutdown
    print("👋 SnapStash shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Zero-config private photo cloud",
    lifespan=lifespan,
)

# CORS — allow all origins for LAN use
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(sync.router)
app.include_router(storage.router)
app.include_router(welcome.router)


# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.app_version}
