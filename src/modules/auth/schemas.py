from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from src.models.user import UserRole
from datetime import datetime
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=100, min_length=1)
    last_name: str = Field(..., max_length=100, min_length=1)
    email: EmailStr = Field(..., max_length=256)
    password: str = Field(..., min_length=8, max_length=256)
    date_of_birth: datetime
    mobile_number: str = Field(..., max_length=15, min_length=10)
    role: UserRole

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise AppError(ErrorCodes.BAD_REQUEST,
                           "Password must be at least of 8 characters length")
        if not any(char.isdigit() for char in v):
            raise AppError(ErrorCodes.BAD_REQUEST,
                           "Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise AppError(
                ErrorCodes.BAD_REQUEST,
                "Password must contain at least one upper case letter")
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        # Normalize datetime to UTC if it has timezone info, otherwise treat as naive
        if v.tzinfo is not None:
            # If timezone-aware, convert to UTC
            v_normalized = v.replace(tzinfo=None)
        else:
            # If timezone-naive, use as is
            v_normalized = v

        # Define minimum date (January 1, 1960) - timezone naive
        min_date = datetime(1960, 1, 1)
        # Get current date - timezone naive
        max_date = datetime.now()

        # Check if date is before 1960
        if v_normalized < min_date:
            raise AppError(ErrorCodes.BAD_REQUEST,
                           "Date of birth cannot be before 1960")

        # Check if date is in the future
        if v_normalized > max_date:
            raise AppError(ErrorCodes.BAD_REQUEST,
                           "Date of birth cannot be in the future")

        return v


class LoginResponse(BaseModel):
    token: str
    first_name: str
    last_name: str


class TokenData(BaseModel):
    sub: str
    role: str
    exp: Optional[int] = None  # Expiration timestamp


class UserLogin(BaseModel):
    email: EmailStr
    password: str
