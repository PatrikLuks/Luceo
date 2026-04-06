import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Import all routers
from src.api.router import all_routers
from src.core.config import settings, validate_production_settings
from src.core.database import engine
from src.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from src.core.rate_limit import limiter

logger = logging.getLogger("luceo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Luceo API starting up (env=%s)", settings.app_env)
    yield
    await engine.dispose()
    logger.info("Luceo API shutting down")


APP_VERSION = "0.2.0"


app = FastAPI(
    title="Luceo API",
    version=APP_VERSION,
    description="AI-powered addiction recovery support platform",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
)

_cors_origins = (
    ["http://localhost:3000", "http://localhost:8081"]
    if settings.app_env == "development"
    else [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
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

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# --- Global exception handlers ---


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning("Validation error on %s: %s", request.url.path, exc.error_count())
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "type": "validation_error"},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "database_error"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"},
    )


@app.get("/health", summary="Health check")
async def health():
    """Health check with optional DB connectivity probe."""
    db_ok = False
    try:
        from src.core.database import async_session_maker
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    return {
        "status": "ok" if db_ok else "degraded",
        "version": APP_VERSION,
        "database": "connected" if db_ok else "unavailable",
    }
