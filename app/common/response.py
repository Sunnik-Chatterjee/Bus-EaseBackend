from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = {}

class ResponseHelper:
    """Helper class to create consistent API responses"""
    
    @staticmethod
    def success_response(message: str, data: Any = {}) -> dict:
        """Create a successful response"""
        return {
            "success": True,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error_response(message: str, data: Any = {}) -> dict:
        """Create an error response"""
        return {
            "success": False,
            "message": message,
            "data": data
        }
