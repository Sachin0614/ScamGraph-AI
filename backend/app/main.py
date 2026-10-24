"""
ScamGraph AI - Main FastAPI Application
Entry point for the backend REST API, static files, and database initialization.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.config import settings
from app.database.session import init_db, SessionLocal
from app.database.seed_data import seed_sample_investigations
from app.routers import (
    investigations_router,
    graph_router,
    evidence_router,
    safety_router,
    settings_router,
    dashboard_router,
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scamgraph.api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Scam Investigation Platform - Threat Graph & Evidence Intelligence Engine",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
app.include_router(investigations_router, prefix=settings.API_V1_STR)
app.include_router(graph_router, prefix=settings.API_V1_STR)
app.include_router(evidence_router, prefix=settings.API_V1_STR)
app.include_router(safety_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    """Initializes database schema and loads sample threat data on startup."""
    logger.info("Initializing ScamGraph AI database...")
    init_db()
    with SessionLocal() as db:
        seed_sample_investigations(db)
    logger.info("ScamGraph AI database initialized and sample dataset verified.")


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for container and uptime monitors."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/api", tags=["Root"])
def api_root():
    """API information endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_docs": "/docs",
        "api_prefix": settings.API_V1_STR,
    }


# Serve compiled frontend production build if available
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json", "health", "api"):
            return None
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/", tags=["Root"])
    def root():
        """Root endpoint when frontend build is not present."""
        return {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "api_docs": "/docs",
            "api_prefix": settings.API_V1_STR,
        }
