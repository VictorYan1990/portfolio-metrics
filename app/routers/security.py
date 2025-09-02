from enum import Enum
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date  # Add date import
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

router = APIRouter(prefix="/securities", tags=["securities"])

# Pydantic Models
class SecuritySecType(Enum):
    stock = "S"
    bond = "B"
    fund = "F"
    index = "I"
    option = "O"
    Undefined = "U"


class SecurityBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    sec_type: Optional[SecuritySecType] = SecuritySecType.Undefined
    description: Optional[str] = None


class SecurityCreate(SecurityBase):
    pass

class SecurityResponse(SecurityBase):

    date_of_creation: Optional[date] = None  # Use date, not datetime.date


@router.post("/", response_model=SecurityResponse, status_code=status.HTTP_201_CREATED)
async def create_security(security_data: SecurityCreate):
    """Create a new security in the database."""
    
    # Validate mandatory fields
    if not security_data.symbol or not security_data.symbol.strip():
        raise handle_validation_error("symbol", "Symbol is mandatory and cannot be empty")

    try:
        # Get database session
        db = next(get_db('sec_master'))
        
        # Check if security already exists (Symbol should be unique)
        existing_security = db.execute(
            text("SELECT 1 FROM securities WHERE symbol = :symbol"),
            {'symbol': security_data.symbol.strip()}
        ).fetchone()

        if existing_security:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Security with symbol '{security_data.symbol}' already exists"
            )

        # Insert new security
        result = db.execute(
            text("""
                INSERT INTO securities (symbol, company_name, sec_type, description)
                VALUES (:symbol, :company_name, :sec_type, :description)
                RETURNING symbol, company_name, sec_type, description, date_of_creation
            """),
            {
                'symbol': security_data.symbol.strip(),
                'company_name': security_data.company_name.strip() if security_data.company_name else None,
                'sec_type': security_data.sec_type.value if security_data.sec_type else None,  # Use .value
                'description': security_data.description.strip() if security_data.description else None
            }
        )
        
        # Fetch the inserted record
        new_security = result.fetchone()
        
        # Commit the transaction
        db.commit()
        
        logger.info(f"Security created successfully: Symbol={security_data.symbol}")
        
        return SecurityResponse(
            symbol=new_security[0],
            company_name=new_security[1],
            sec_type=new_security[2],
            description=new_security[3],
            date_of_creation=new_security[4]
        )

    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating security: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data provided for security creation"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating security: {e}")
        raise handle_database_error(e, "security creation")

@router.get("/", response_model=List[SecurityResponse])
async def get_securities():
    """Get all securities."""
    try:
        db = next(get_db('sec_master'))
        
        result = db.execute(
            text("SELECT symbol, company_name, sec_type, description, date_of_creation FROM securities")
        )
        
        securities: List[SecurityResponse] = []
        for row in result.fetchall():
            securities.append(SecurityResponse(
                symbol=row[0],
                company_name=row[1],
                sec_type=row[2],
                description=row[3],
                date_of_creation=row[4]
            ))
        
        return securities

    except Exception as e:
        logger.error(f"Error retrieving securities: {e}")
        raise handle_database_error(e, "retrieving securities")

@router.get("/{symbol}", response_model=SecurityResponse)
async def get_security_by_symbol(symbol: str):
    """Get a specific security by symbol."""
    try:
        db = next(get_db('sec_master'))
        
        result = db.execute(
            text("SELECT symbol, company_name, sec_type, description, date_of_creation FROM securities WHERE symbol = :symbol"),
            {'symbol': symbol}
        ).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Security with symbol '{symbol}' not found"
            )

        return SecurityResponse(
            symbol=result[0],
            company_name=result[1],
            sec_type=result[2],
            description=result[3],
            date_of_creation=result[4]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving security by symbol: {e}")
        raise handle_database_error(e, "retrieving security")