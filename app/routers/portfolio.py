from re import S
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

router = APIRouter()

# Pydantic models
class PortfolioBase(BaseModel):
    id: str
    name: str
    owner_id: str
    description: Optional[str] = None
    benchmark: Optional[str] = None
    base_currency: Optional[str] = None
    meta_data: Optional[dict] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):

    created_at: date
    updated_at: date



class PortfolioSnapshot(BaseModel):
    id: str
    as_of_date: date
    balance: float
    is_active: bool
    meta_data: Optional[dict] = None


# Mock data storage (replace with database in production)
portfolios = []
portfolio_id_counter = 1

@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios():
    """Get all portfolios"""
    return portfolios

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int):
    """Get a specific portfolio by ID"""
    portfolio = next((p for p in portfolios if p["id"] == portfolio_id), None)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return portfolio

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: PortfolioCreate):
    """Create a new portfolio"""
    global portfolio_id_counter
    
    new_portfolio = PortfolioResponse(
        id=portfolio_id_counter,
        **portfolio.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    portfolios.append(new_portfolio.dict())
    portfolio_id_counter += 1
    
    return new_portfolio

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(portfolio_id: int, portfolio_update: PortfolioCreate):
    """Update an existing portfolio"""
    portfolio_index = next((i for i, p in enumerate(portfolios) if p["id"] == portfolio_id), None)
    
    if portfolio_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    updated_portfolio = PortfolioResponse(
        id=portfolio_id,
        **portfolio_update(),
        created_at=portfolios[portfolio_index]["created_at"],
        updated_at=datetime.now()
    )
    
    portfolios[portfolio_index] = updated_portfolio.dict()
    return updated_portfolio

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: int):
    """Delete a portfolio"""
    portfolio_index = next((i for i, p in enumerate(portfolios) if p["id"] == portfolio_id), None)
    
    if portfolio_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    portfolios.pop(portfolio_index)
