import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.v1.health import router as health_router
from app.api.v1.tickets import router as tickets_router
from app.core.config import get_settings
from app.core.database import create_db_and_tables, engine
from app.core.logging import configure_logging
from app.db.seed import seed_demo_data

configure_logging()

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.app_name)

    create_db_and_tables()

    if settings.enable_demo_seed:
        with Session(engine) as session:
            seed_demo_data(session)

    yield

    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="AI-powered support ticket triage and workflow automation platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(tickets_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "SupportDesk AI backend is running",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
        "tickets": f"{settings.api_v1_prefix}/tickets",
    }