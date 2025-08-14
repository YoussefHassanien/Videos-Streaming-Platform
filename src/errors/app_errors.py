from fastapi import HTTPException
from .error_codes import ErrorCodes

class AppError(HTTPException):
    def __init__(self, error_code: ErrorCodes, custom_message: str | None = None, custom_status: int | None = None):
        """
        Create an AppError from an ErrorCode enum value
        
        Args:
            error_code: The ErrorCodes enum value
            custom_message: Optional custom message to override the default
            custom_status: Optional custom status to override the default
        """
        code_obj = error_code.value  # Get the ErrorCode object from the enum
        
        super().__init__(
            status_code=custom_status or code_obj.status,
            detail=custom_message or code_obj.message
        )
        
        self.error_code = error_code
        self.original_status = code_obj.status
        self.original_message = code_obj.message