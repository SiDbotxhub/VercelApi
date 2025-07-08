from lib.config import Config
from fastapi import HTTPException
from typing import Optional

def validate_api_key(api_key: str) -> bool:
    """Validate the provided API key against configured keys"""
    if not Config.API_KEYS or not api_key:
        return False
    return api_key in Config.API_KEYS

def create_error_response(
    message: str, 
    status_code: int = 400,
    details: Optional[dict] = None
) -> HTTPException:
    """Helper to create consistent error responses"""
    error_info = {
        "error": message,
        "status": "failed"
    }
    if details:
        error_info["details"] = details
    
    return HTTPException(
        status_code=status_code,
        detail=error_info
    )
