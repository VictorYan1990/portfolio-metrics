from pydantic import BaseModel, validator
from typing import Optional
import re

class PasswordValidator:
    """Password validation utilities."""
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

class UserDataValidator(BaseModel):
    """User data validation model."""
    
    username: str
    email: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not PasswordValidator.validate_email(v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not PasswordValidator.validate_password_strength(v):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, and number')
        return v
