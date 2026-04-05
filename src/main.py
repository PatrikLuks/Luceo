import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import engine

# Import all routers
from src.api.router import all_routers

logger = logging.getLogger("luceo")


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
