import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_portfolio():
    """Test creating a new portfolio"""
    portfolio_data = {
        "name": "Test Portfolio",
        "description": "A test portfolio",
        "initial_balance": 10000.00
    }
    
    response = client.post("/api/v1/portfolio/", json=portfolio_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == portfolio_data["name"]
    assert data["description"] == portfolio_data["description"]
    assert data["initial_balance"] == portfolio_data["initial_balance"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_portfolios():
    """Test getting all portfolios"""
    response = client.get("/api/v1/portfolio/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_get_portfolio():
    """Test getting a specific portfolio"""
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio 2",
        "description": "Another test portfolio",
        "initial_balance": 5000.00
    }
    
    create_response = client.post("/api/v1/portfolio/", json=portfolio_data)
    portfolio_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/v1/portfolio/{portfolio_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == portfolio_id
    assert data["name"] == portfolio_data["name"]

def test_get_portfolio_not_found():
    """Test getting a non-existent portfolio"""
    response = client.get("/api/v1/portfolio/999")
    assert response.status_code == 404

def test_update_portfolio():
    """Test updating a portfolio"""
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio 3",
        "description": "A test portfolio to update",
        "initial_balance": 7500.00
    }
    
    create_response = client.post("/api/v1/portfolio/", json=portfolio_data)
    portfolio_id = create_response.json()["id"]
    
    # Update it
    update_data = {
        "name": "Updated Portfolio",
        "description": "Updated description",
        "initial_balance": 8000.00
    }
    
    response = client.put(f"/api/v1/portfolio/{portfolio_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["initial_balance"] == update_data["initial_balance"]

def test_delete_portfolio():
    """Test deleting a portfolio"""
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio 4",
        "description": "A test portfolio to delete",
        "initial_balance": 3000.00
    }
    
    create_response = client.post("/api/v1/portfolio/", json=portfolio_data)
    portfolio_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/v1/portfolio/{portfolio_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/portfolio/{portfolio_id}")
    assert get_response.status_code == 404
