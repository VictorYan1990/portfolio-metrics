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

router = APIRouter(prefix="/instruments", tags=["financial-instruments"])

# Pydantic Models
class InstrumentType(Enum):
    stock = "S"
    bond = "B"
    fund = "F"
    index = "I"
    option = "O"
    Undefined = "U"

class InstrumentBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    instrument_type: Optional[InstrumentType] = InstrumentType.Undefined
    description: Optional[str] = None

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentResponse(InstrumentBase):
    date_of_creation: Optional[date] = None

@router.post("/", response_model=InstrumentResponse, status_code=status.HTTP_201_CREATED)
async def create_instrument(instrument_data: InstrumentCreate):
    """Create a new financial instrument in the database."""
    
    # Validate mandatory fields
    if not instrument_data.symbol or not instrument_data.symbol.strip():
        raise handle_validation_error("symbol", "Symbol is mandatory and cannot be empty")

    try:
        # Get database session
        db = next(get_db('sec_master'))
        
        # Check if instrument already exists (Symbol should be unique)
        existing_instrument = db.execute(
            text("SELECT 1 FROM securities WHERE symbol = :symbol"),
            {'symbol': instrument_data.symbol.strip()}
        ).fetchone()

        if existing_instrument:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Instrument with symbol '{instrument_data.symbol}' already exists"
            )

        # Insert new instrument
        result = db.execute(
            text("""
                INSERT INTO securities (symbol, company_name, sec_type, description)
                VALUES (:symbol, :company_name, :sec_type, :description)
                RETURNING symbol, company_name, sec_type, description, date_of_creation
            """),
            {
                'symbol': instrument_data.symbol.strip(),
                'company_name': instrument_data.company_name.strip() if instrument_data.company_name else None,
                'sec_type': instrument_data.instrument_type.value if instrument_data.instrument_type else None,
                'description': instrument_data.description.strip() if instrument_data.description else None
            }
        )
        
        # Fetch the inserted record
        new_instrument = result.fetchone()
        
        # Commit the transaction
        db.commit()
        
        logger.info(f"Instrument created successfully: Symbol={instrument_data.symbol}")
        
        return InstrumentResponse(
            symbol=new_instrument[0],
            company_name=new_instrument[1],
            instrument_type=new_instrument[2],
            description=new_instrument[3],
            date_of_creation=new_instrument[4]
        )

    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating instrument: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data provided for instrument creation"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating instrument: {e}")
        raise handle_database_error(e, "instrument creation")

@router.get("/", response_model=List[InstrumentResponse])
async def get_instruments():
    """Get all financial instruments."""
    try:
        db = next(get_db('sec_master'))
        
        result = db.execute(
            text("SELECT symbol, company_name, sec_type, description, date_of_creation FROM securities")
        )
        
        instruments: List[InstrumentResponse] = []
        for row in result.fetchall():
            instruments.append(InstrumentResponse(
                symbol=row[0],
                company_name=row[1],
                instrument_type=row[2],
                description=row[3],
                date_of_creation=row[4]
            ))
        
        return instruments

    except Exception as e:
        logger.error(f"Error retrieving instruments: {e}")
        raise handle_database_error(e, "retrieving instruments")

@router.get("/{symbol}", response_model=InstrumentResponse)
async def get_instrument_by_symbol(symbol: str):
    """Get a specific financial instrument by symbol."""
    try:
        db = next(get_db('sec_master'))
        
        result = db.execute(
            text("SELECT symbol, company_name, sec_type, description, date_of_creation FROM securities WHERE symbol = :symbol"),
            {'symbol': symbol}
        ).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instrument with symbol '{symbol}' not found"
            )

        return InstrumentResponse(
            symbol=result[0],
            company_name=result[1],
            instrument_type=result[2],
            description=result[3],
            date_of_creation=result[4]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving instrument by symbol: {e}")
        raise handle_database_error(e, "retrieving instrument")

@router.put("/{symbol}", response_model=InstrumentResponse)
async def update_instrument(symbol: str, instrument_data: InstrumentCreate):
    """Update an existing financial instrument."""
    try:
        db = next(get_db('sec_master'))
        
        # Check if instrument exists
        existing = db.execute(
            text("SELECT 1 FROM securities WHERE symbol = :symbol"),
            {'symbol': symbol}
        ).fetchone()

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instrument with symbol '{symbol}' not found"
            )

        # Update the instrument
        result = db.execute(
            text("""
                UPDATE securities 
                SET company_name = :company_name, sec_type = :sec_type, 
                    description = :description
                WHERE symbol = :symbol
                RETURNING symbol, company_name, sec_type, description, date_of_creation
            """),
            {
                'symbol': symbol,
                'company_name': instrument_data.company_name.strip() if instrument_data.company_name else None,
                'sec_type': instrument_data.instrument_type.value if instrument_data.instrument_type else None,
                'description': instrument_data.description.strip() if instrument_data.description else None
            }
        )
        
        updated_instrument = result.fetchone()
        db.commit()
        
        logger.info(f"Instrument updated successfully: Symbol={symbol}")
        
        return InstrumentResponse(
            symbol=updated_instrument[0],
            company_name=updated_instrument[1],
            instrument_type=updated_instrument[2],
            description=updated_instrument[3],
            date_of_creation=updated_instrument[4]
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating instrument: {e}")
        raise handle_database_error(e, "updating instrument")

@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instrument(symbol: str):
    """Delete a financial instrument."""
    try:
        db = next(get_db('sec_master'))
        
        result = db.execute(
            text("DELETE FROM securities WHERE symbol = :symbol"),
            {'symbol': symbol}
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instrument with symbol '{symbol}' not found"
            )
        
        db.commit()
        logger.info(f"Instrument deleted successfully: Symbol={symbol}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting instrument: {e}")
        raise handle_database_error(e, "deleting instrument")
