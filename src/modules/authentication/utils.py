from datetime import datetime, timedelta, timezone
from typing import Optional
from src.modules.authentication.schemas import TokenData
from jose import jwt
from src.configs.settings import settings

def create_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token with expiration time
    
    Args:
        data: Token data to encode
        expires_delta: Optional custom expiration time. If None, uses default from settings
    
    Returns:
        Encoded JWT token string
    """
    data_copy = data.model_dump()  # Convert Pydantic model to dict
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Use default expiration from settings (e.g., 30 minutes)
        expire = datetime.now(timezone.utc) + timedelta(minutes=getattr(settings, 'access_token_expire_minutes', 30))
    
    # Add expiration to token payload
    data_copy.update({"exp": expire})
    
    token = jwt.encode(data_copy, settings.access_token_secret_key, algorithm=settings.access_token_algorithm)
    return token