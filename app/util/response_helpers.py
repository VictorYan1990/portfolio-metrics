from fastapi import HTTPException, status
from typing import Any, Dict, Optional
import logging

def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response."""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response

def create_error_response(message: str, status_code: int = 400, details: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {"success": False, "message": message}
    if details:
        response["details"] = details
    return response

def handle_database_error(error: Exception, operation: str = "database operation") -> HTTPException:
    """Handle database errors and return appropriate HTTP exception."""
    logging.error(f"Database error during {operation}: {error}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database error during {operation}"
    )

def handle_validation_error(field: str, message: str) -> HTTPException:
    """Handle validation errors and return appropriate HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Validation error for {field}: {message}"
    )

def handle_not_found_error(resource: str, identifier: str) -> HTTPException:
    """Handle not found errors and return appropriate HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} with {identifier} not found"
    )

def handle_unauthorized_error(message: str = "Unauthorized access") -> HTTPException:
    """Handle unauthorized errors and return appropriate HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message
    )
