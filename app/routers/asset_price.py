from enum import Enum
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

# Import utility functions
from app.util.database import get_db
from app.util.response_helpers import (
    create_success_response, 
    handle_database_error, 
    handle_validation_error
)
from app.util.logger import logger

router = APIRouter(prefix="/instruments/price", tags=["Market Data of Financial-Instruments"])


