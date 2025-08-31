from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import math

router = APIRouter()

# Pydantic models
class MetricBase(BaseModel):
    portfolio_id: int
    date: date
    value: float
    metric_type: str

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PortfolioMetrics(BaseModel):
    portfolio_id: int
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float

# Mock data storage (replace with database in production)
metrics = []
metric_id_counter = 1

@router.get("/", response_model=List[Metric])
async def get_metrics(portfolio_id: Optional[int] = None):
    """Get all metrics or filter by portfolio_id"""
    if portfolio_id:
        return [m for m in metrics if m["portfolio_id"] == portfolio_id]
    return metrics

@router.get("/{metric_id}", response_model=Metric)
async def get_metric(metric_id: int):
    """Get a specific metric by ID"""
    metric = next((m for m in metrics if m["id"] == metric_id), None)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )
    return metric

@router.post("/", response_model=Metric, status_code=status.HTTP_201_CREATED)
async def create_metric(metric: MetricCreate):
    """Create a new metric"""
    global metric_id_counter
    
    new_metric = Metric(
        id=metric_id_counter,
        **metric.dict(),
        created_at=datetime.now()
    )
    
    metrics.append(new_metric.dict())
    metric_id_counter += 1
    
    return new_metric

@router.get("/portfolio/{portfolio_id}/summary", response_model=PortfolioMetrics)
async def get_portfolio_summary(portfolio_id: int):
    """Get portfolio performance summary"""
    portfolio_metrics = [m for m in metrics if m["portfolio_id"] == portfolio_id]
    
    if not portfolio_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found for this portfolio"
        )
    
    # Calculate basic metrics (simplified calculations)
    values = [m["value"] for m in portfolio_metrics]
    
    if len(values) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 2 data points for calculations"
        )
    
    # Calculate total return
    total_return = ((values[-1] - values[0]) / values[0]) * 100
    
    # Calculate annualized return (simplified)
    days = (portfolio_metrics[-1]["date"] - portfolio_metrics[0]["date"]).days
    annualized_return = ((values[-1] / values[0]) ** (365 / days) - 1) * 100 if days > 0 else 0
    
    # Calculate volatility (standard deviation)
    mean_value = sum(values) / len(values)
    variance = sum((x - mean_value) ** 2 for x in values) / len(values)
    volatility = math.sqrt(variance)
    
    # Calculate Sharpe ratio (simplified, assuming risk-free rate = 0)
    sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
    
    # Calculate max drawdown
    max_drawdown = 0
    peak = values[0]
    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return PortfolioMetrics(
        portfolio_id=portfolio_id,
        total_return=round(total_return, 2),
        annualized_return=round(annualized_return, 2),
        volatility=round(volatility, 2),
        sharpe_ratio=round(sharpe_ratio, 2),
        max_drawdown=round(max_drawdown * 100, 2)
    )

@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metric(metric_id: int):
    """Delete a metric"""
    metric_index = next((i for i, m in enumerate(metrics) if m["id"] == metric_id), None)
    
    if metric_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )
    
    metrics.pop(metric_index)
