from fastapi import APIRouter
from app.routers import portfolio, metrics

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
