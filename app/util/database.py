import os
import hmac
import hashlib
import base64
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
import logging
from app.core.config import settings

# Database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """Get a single database session."""
    return SessionLocal()

SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
ACCESS_TOKEN_EXPIRE_HOURS = 1

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(username: str) -> str:
    """Generate a JWT-like token with expiration."""
    expiration = (datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).strftime('%Y-%m-%d %H:%M:%S')
    payload = f"{username}|{expiration}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = f"{payload}|{signature}"
    return base64.urlsafe_b64encode(token.encode()).decode()

def verify_token(token: str) -> Optional[str]:
    """Verify a token's validity."""
    logging.debug(f'Verifying token: {token}')
    try:
        decoded_token = base64.urlsafe_b64decode(token).decode()
        username, expiration, signature = decoded_token.rsplit('|', 2)
        payload = f"{username}|{expiration}"
        expected_signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

        if hmac.compare_digest(signature, expected_signature):
            if datetime.utcnow() < datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S'):
                return username
            else:
                logging.debug("Token valid but expired")
        else:
            logging.debug("Token signature not valid")
    except Exception as e:
        logging.info(f"Token verification exception: {e}")
    return None
