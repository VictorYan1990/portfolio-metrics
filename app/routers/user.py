from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# Security
security = HTTPBearer()

# Pydantic Models (converted from forms.py)
class UserLoginForm(BaseModel):
    email: EmailStr
    password: str

class UserRegistrationForm(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str]

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: str = Depends(get_current_user)):
    """Get current user profile information."""
    # This endpoint uses the same logic as auth.py get_current_user_info
    # You can either duplicate the logic here or create a shared service
    try:
        # Implementation would be similar to auth.py get_current_user_info
        # For now, returning a placeholder
        return UserProfile(
            id=1,
            username=current_user,
            email=f"{current_user}@example.com",
            roles=["user"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {e}"
        )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: dict,
    current_user: str = Depends(get_current_user)
):
    """Update current user profile information."""
    try:
        # Implementation for updating user profile
        # This would involve database operations
        return UserProfile(
            id=1,
            username=current_user,
            email=profile_data.get("email", f"{current_user}@example.com"),
            roles=["user"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {e}"
        )

@router.get("/", response_model=List[UserProfile])
async def get_all_users(current_user: str = Depends(get_current_user)):
    """Get all users (admin only)."""
    try:
        # Check if current user has admin role
        # Implementation would check user roles from database
        
        # For now, returning placeholder data
        return [
            UserProfile(
                id=1,
                username="admin",
                email="admin@example.com",
                roles=["admin"]
            ),
            UserProfile(
                id=2,
                username="user",
                email="user@example.com",
                roles=["user"]
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {e}"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: str = Depends(get_current_user)
):
    """Delete a user (admin only)."""
    try:
        # Check if current user has admin role
        # Implementation would delete user from database
        
        # For now, just return success
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {e}"
        )
