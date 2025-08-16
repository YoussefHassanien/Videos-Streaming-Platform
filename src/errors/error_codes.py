from enum import Enum

class ErrorCode:
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
    
    def __repr__(self):
        return f"ErrorCode(status={self.status}, message='{self.message}')"

class ErrorCodes(Enum):
    BAD_REQUEST = ErrorCode(400, "One or more of the sent fields is invalid")
    UNAUTHORIZED = ErrorCode(401, "Unauthorized!")
    PERMISSION_NOT_GRANTED = ErrorCode(403, "Permission not granted!")
    NOT_FOUND = ErrorCode(404, "Not found!")
    UPLOAD_TIMEOUT = ErrorCode(408, "Upload processing timeout")
    INTERNAL_SERVER_ERROR = ErrorCode(500, "Internal Server Error")
    EXTERNAL_SERVICE_ERROR = ErrorCode(503, "External service error")

# Create a convenience instance for easy access
error_codes = ErrorCodes