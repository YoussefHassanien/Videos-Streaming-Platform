from enum import Enum

class ErrorCode:
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
    
    def __repr__(self):
        return f"ErrorCode(status={self.status}, message='{self.message}')"

class ErrorCodes(Enum):
    # User creation errors
    USER_ALREADY_EXISTS = ErrorCode(400, "This user is already registered")

    # Passowrd validation errors
    TOO_SHORT_PASSWORD = ErrorCode(400, "Password must be at least 8 characters")
    ONE_DIGIT_REQUIRED = ErrorCode(400, "Password must contain at least one digit")
    ONE_UPPERCASE_LETTER_REQUIRED = ErrorCode(400, "Password must contain at least one uppercase letter")
    
    # Authentication and authorization errors
    UNAUTHORIZED = ErrorCode(401, "Unauthorized!")
    NO_TOKEN = ErrorCode(400, "No Token Provided!")
    EXPIRED_TOKEN = ErrorCode(401, "Token Expired!")
    INVALID_TOKEN = ErrorCode(401, "Invalid Token!")
    USER_NOT_FOUND = ErrorCode(404, "User not found!")
    PERMISSION_NOT_GRANTED = ErrorCode(403, "Permission not granted!")
    
    # Server errors
    INTERNAL_SERVER_ERROR = ErrorCode(500, "Internal Server Error")

# Create a convenience instance for easy access
error_codes = ErrorCodes