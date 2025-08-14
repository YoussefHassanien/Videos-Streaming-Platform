from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError

from src.configs.settings import settings
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from src.models.user import User, UserRole
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
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        token_data = TokenData(**payload)
        return token_data
        
    except ExpiredSignatureError:
        raise AppError(ErrorCodes.EXPIRED_TOKEN)
    except JWTError:
        raise AppError(ErrorCodes.INVALID_TOKEN)
    except Exception:
        raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR, "JWT token error")

def is_authorized(role: UserRole, user: User = Depends(is_authenticated)) -> TokenData:
    """
    Authorization middleware
    Returns a dependency that checks if the authenticated user has the required role.
    """
    if not user:
        raise AppError(ErrorCodes.USER_NOT_FOUND)
    
    if user.role != role:
        raise AppError(ErrorCodes.PERMISSION_NOT_GRANTED)
    
    return user
