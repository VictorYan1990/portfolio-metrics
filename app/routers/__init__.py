from fastapi import APIRouter
from app.routers import portfolio, auth, user, security

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(portfolio.router, tags=["portfolio"])
api_router.include_router(security.router, tags=["securities"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(user.router, tags=["users"])
