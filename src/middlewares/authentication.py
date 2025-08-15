from typing import Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError

from src.configs.settings import settings
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from src.models.user import UserRole
from src.modules.authentication.schemas import TokenData

security = HTTPBearer()

async def is_authenticated(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Authentication middleware equivalent to the Node.js isAuthenticated function.
    Validates JWT token and returns the authenticated user.
    """
    token = credentials.credentials
    
    if not token:
        raise AppError(ErrorCodes.NO_TOKEN)
    
    try:
        # Verify the JWT token
        payload = jwt.decode(token, settings.access_token_secret_key, algorithms=[settings.access_token_algorithm])
        
        token_data = TokenData(**payload)
        return token_data
        
    except ExpiredSignatureError:
        raise AppError(ErrorCodes.EXPIRED_TOKEN)
    except JWTError:
        raise AppError(ErrorCodes.INVALID_TOKEN)
    except Exception:
        raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR, "JWT token error")

def is_authorized(required_role: UserRole) -> Callable:
    """
    Authorization middleware that returns a dependency function.
    Returns a dependency that checks if the authenticated user has the required role.
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        A dependency function that validates user authorization
    """
    def role_checker(user: TokenData = Depends(is_authenticated)) -> TokenData:
        if not user:
            raise AppError(ErrorCodes.USER_NOT_FOUND)
        
        if user.role != required_role.value:  # Compare with role value
            raise AppError(ErrorCodes.PERMISSION_NOT_GRANTED)
        
        return user
    
    return role_checker
