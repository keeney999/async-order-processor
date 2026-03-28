"""FastAPI application entry point."""

from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "env": settings.ENVIRONMENT}
