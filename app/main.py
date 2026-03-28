"""FastAPI application entry point."""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="Async Order Processor", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "env": settings.ENVIRONMENT}
