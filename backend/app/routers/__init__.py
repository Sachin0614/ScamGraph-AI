from app.routers.investigations import router as investigations_router
from app.routers.graph import router as graph_router
from app.routers.evidence import router as evidence_router
from app.routers.safety import router as safety_router
from app.routers.settings import router as settings_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "investigations_router",
    "graph_router",
    "evidence_router",
    "safety_router",
    "settings_router",
    "dashboard_router",
]
