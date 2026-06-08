from fastapi import APIRouter, status

from app.core.config import get_settings
from app.core.database import check_database_connection

router = APIRouter(prefix="/health", tags=["Health"])

settings = get_settings()


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/db", status_code=status.HTTP_200_OK)
def database_health_check() -> dict[str, str]:
    is_connected = check_database_connection()

    if not is_connected:
        return {
            "status": "error",
            "database": "not connected",
        }

    return {
        "status": "ok",
        "database": "connected",
    }