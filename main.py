"""
TAPI Backend — Entry point.

Start with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.config import settings
from infraestructure.database.postgres.connection import init_postgres, close_postgres
from infraestructure.database.mongodb.connection import init_mongodb, close_mongodb
from infraestructure.cache.redis_cache import init_redis, close_redis


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "TAPI API — Sistema de fidelización y reseñas para tiendas con NFC. "
            "Proporciona endpoints para autenticación, gestión de negocios, "
            "reseñas, programas de lealtad, notificaciones, y métricas."
        ),
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ──────────────────────────────────────────
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

    # ── Health Check ────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "service": "TAPI API"}

    # ── Lifecycle ───────────────────────────────────────
    @app.on_event("startup")
    async def startup():
        await init_postgres()
        await init_mongodb()
        await init_redis()

    @app.on_event("shutdown")
    async def shutdown():
        await close_postgres()
        await close_mongodb()
        await close_redis()

    return app


app = create_app()
