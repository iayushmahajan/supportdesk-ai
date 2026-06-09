from app.api.v1.automation import router as automation_router
from app.api.v1.health import router as health_router
from app.api.v1.tickets import router as tickets_router

__all__ = ["automation_router", "health_router", "tickets_router"]