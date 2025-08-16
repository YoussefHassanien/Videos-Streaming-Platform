from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError

from src.configs.settings import settings
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes
from src.models.user import UserRole
from src.modules.auth.schemas import TokenData

security = HTTPBearer()

class Auth:
    """
    Unified Authentication and Authorization class
    Handles both JWT token validation and role-based access control
    """
    
    def __init__(self, required_role: UserRole):
        """
        Initialize Auth with role requirement
        
        Args:
            required_role: Enforce role-based authorization
        """
        self.required_role = required_role
    
    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
        """
        Authenticate user and authorize based on role
        
        Args:
            credentials: JWT credentials from request header
            
        Returns:
            TokenData: Authenticated and authorized user data
            
        Raises:
            AppError: If authentication or authorization fails
        """
        # Step 1: Authentication
        user = self._authenticate(credentials)
        
        # Step 2: Authorization
        self._authorize(user)
        
        return user
    
    def _authenticate(self, credentials: HTTPAuthorizationCredentials) -> TokenData:
        """
        Validate JWT token and extract user data
        
        Args:
            credentials: JWT credentials from request header
            
        Returns:
            TokenData: Authenticated user data
            
        Raises:
            AppError: If token is invalid, expired, or missing
        """
        token = credentials.credentials
        
        if not token:
            raise AppError(ErrorCodes.BAD_REQUEST, "No token provided!")
        
        try:
            # Verify the JWT token
            payload = jwt.decode(
                token, 
                settings.access_token_secret_key, 
                algorithms=[settings.access_token_algorithm]
            )
            
            token_data = TokenData(**payload)
            return token_data
            
        except ExpiredSignatureError:
            raise AppError(ErrorCodes.UNAUTHORIZED, "Token is expired!")
        except JWTError:
            raise AppError(ErrorCodes.UNAUTHORIZED, "Invalid token!")
        except Exception:
            raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR, "JWT token error")
    
    def _authorize(self, user: TokenData) -> None:
        """
        Check if user has required role
        
        Args:
            user: Authenticated user data
            
        Raises:
            AppError: If user doesn't have required role
        """
        if not user:
            raise AppError(ErrorCodes.NOT_FOUND, "User not found!")
        
        if user.role != self.required_role.value:
            raise AppError(ErrorCodes.PERMISSION_NOT_GRANTED)
