"""Custom exception classes."""
from fastapi import HTTPException, status

class DatabaseError(HTTPException):
    """Database operation error."""
    def __init__(self, detail: str) -> None:
        """Initialize database error."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}"
        )

class ValidationError(HTTPException):
    """Data validation error."""
    def __init__(self, detail: str) -> None:
        """Initialize validation error."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {detail}"
        )