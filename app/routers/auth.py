from fastapi import APIRouter, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

# Import utility functions
from app.util.database import get_db
from app.util.security import hash_password, verify_password, generate_token, verify_token
from app.util.response_helpers import (
    create_success_response, 
    handle_database_error, 
    handle_validation_error,
    handle_not_found_error,
    handle_unauthorized_error
)
from app.util.logger import logger

router = APIRouter(prefix="/auth", tags=["authentication"])

# Security
security = HTTPBearer()

# Pydantic Models
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str]

class TokenResponse(BaseModel):
    message: str
    token: str
    roles: List[str]

class TokenVerifyResponse(BaseModel):
    message: str
    username: Optional[str] = None

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token."""
    token = credentials.credentials
    username = verify_token(token)
    if not username:
        raise handle_unauthorized_error("Invalid or expired token")
    return username

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Authenticate user and return a token."""
    username = user_data.username
    password = user_data.password

    if not username or not password:
        raise handle_validation_error("credentials", "Username and password are required")

    try:
        # Get database session
        db = next(get_db('user_data'))
        
        # Query the users table for username
        logger.debug(f"Querying user for login: {username}")
        result = db.execute(
            text("SELECT id, password_hash FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()

        if not result:
            raise handle_unauthorized_error("Invalid credentials")

        user_id, stored_password_hash = result[0], result[1]

        # Verify the provided password against the stored hash
        if verify_password(password, stored_password_hash):
            # Generate token
            token = generate_token(username)

            # Query roles for the user
            roles = db.execute(
                text("""
                    SELECT r.role_name
                    FROM user_role_mapping urm
                    JOIN user_role r ON urm.role_id = r.id
                    WHERE urm.user_id = :user_id
                """),
                {'user_id': user_id}
            ).fetchall()

            # Collect role names
            role_names = [role[0] for role in roles]

            return TokenResponse(
                message="Login successful",
                token=token,
                roles=role_names
            )
        else:
            raise handle_unauthorized_error("Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise handle_database_error(e, "login")

@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token_endpoint(authorization: str = Header(None)):
    """Verify if a token is valid."""
    logger.debug('Received /auth/verify request')
    
    if not authorization:
        raise handle_unauthorized_error("Token missing")

    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(' ')[1]
    except IndexError:
        raise handle_unauthorized_error("Malformed token")

    username = verify_token(token)
    if username:
        return TokenVerifyResponse(
            message="Token valid",
            username=username
        )
    
    raise handle_unauthorized_error("Invalid or expired token")

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user with the given username, email, and password."""
    username = user_data.username
    email = user_data.email
    password = user_data.password

    if not username or not email or not password:
        raise handle_validation_error("credentials", "Username, email, and password are required")

    hashed_password = hash_password(password)

    try:
        db = next(get_db('user_data'))
        
        # Start transaction
        with db.begin():
            # Check if username or email already exists
            user_exists = db.execute(
                text("SELECT 1 FROM users WHERE username = :username OR email = :email"),
                {'username': username, 'email': email}
            ).fetchone()

            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username or email already exists!"
                )

            # Insert new user
            db.execute(
                text("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)"),
                {'username': username, 'email': email, 'password_hash': hashed_password}
            )

            # Query the new user's ID
            user_id = db.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {'username': username}
            ).fetchone()[0]

            # Query the role ID for 'viewer'
            role_id = db.execute(
                text("SELECT id FROM user_role WHERE role_name = 'viewer'")
            ).fetchone()[0]

            # Insert into user_role_mapping
            db.execute(
                text("INSERT INTO user_role_mapping (user_id, role_id) VALUES (:user_id, :role_id)"),
                {'user_id': user_id, 'role_id': role_id}
            )

        return create_success_response(message="User created successfully")

    except HTTPException:
        raise
    except IntegrityError:
        raise handle_database_error(Exception("Integrity error"), "user creation")
    except Exception as e:
        logger.error(f"Transaction rolled back due to: {e}")
        raise handle_database_error(e, "user creation")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current user information."""
    try:
        db = next(get_db('user_data'))
        
        # Get user info
        user_result = db.execute(
            text("SELECT id, username, email FROM users WHERE username = :username"),
            {'username': current_user}
        ).fetchone()

        if not user_result:
            raise handle_not_found_error("User", f"username '{current_user}'")

        user_id, username, email = user_result

        # Get user roles
        roles = db.execute(
            text("""
                SELECT r.role_name
                FROM user_role_mapping urm
                JOIN user_role r ON urm.role_id = r.id
                WHERE urm.user_id = :user_id
            """),
            {'user_id': user_id}
        ).fetchall()

        role_names = [role[0] for role in roles]

        return UserResponse(
            id=user_id,
            username=username,
            email=email,
            roles=role_names
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise handle_database_error(e, "retrieving user information")
