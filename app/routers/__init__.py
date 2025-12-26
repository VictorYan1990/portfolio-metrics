from fastapi import APIRouter
from app.routers import portfolio, instruments, auth

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(instruments.router, prefix="/instruments", tags=["financial-instruments"])
api_router.include_router(auth.router, tags=["authentication"])
