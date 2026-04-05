import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings, validate_production_settings
from src.core.database import engine
from src.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware

# Import all routers
from src.api.router import all_routers

logger = logging.getLogger("luceo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Luceo API starting up (env=%s)", settings.app_env)
    yield
    await engine.dispose()
    logger.info("Luceo API shutting down")


app = FastAPI(
    title="Luceo API",
    version="0.1.0",
    description="AI-powered addiction recovery support platform",
    lifespan=lifespan,
)

_cors_origins = (
    ["http://localhost:3000", "http://localhost:8081"]
    if settings.app_env == "development"
    else [f"https://{origin}" for origin in settings.cors_allowed_origins.split(",") if origin]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in all_routers:
    app.include_router(router)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
